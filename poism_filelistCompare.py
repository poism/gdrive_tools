import sys, csv, string, datetime
# Expects 2 args, source.completelist.csv and search-in.completelist.csv
# This script is intended to compare two csv outputs from poism_getFolderFileList.sh
# This will output a final csv that compares the srcFile to the searchFile.
# Results include: PATH_MATCH, IDENTICAL, MOVED, RENAMED, CHANGED, and MISSING (in the searchFile).
# Note, files existing in searchFile but NOT in the srcFile are completely ignored
# - this is a one-way verification only, just run again and swap the srcFile and the searchFile if you wish...
# For instance, use this to compare a current folder structure with an old backup of the same hierarchy... or to check data migration.
# Can for static backups, can also be checked against old completelist.csv to detect bitrot.
# Po@poism.com

# CONFIGURABLES:
checkHash = True
includeNameMatches = True  # NOTE This will include "NAME_MATCH" Type, which shows files with matching names, regardless of directory (only if other more specific matches fail).

try:
	srcFileName = sys.argv[1]
	searchFileName = sys.argv[2]
except:
	print "Requires two arguments be provided (two output files from poism_getFolderFileList.sh)!"
	print "eg. './path/to/source.completelist.csv' './path/to/search-in.completelist.csv'"
	print "Note, this performs a one-directional comparison, the source should be the LONGER file list."
	print "Files that exist in search-in but not in source are ignored."
	print "Hint: pointing to the same completelist.csv for both source and search, will identify duplicates ('MOVED') items."
	sys.exit(1)

# This MUST be the LONGER filelist csv! Each line in this file will be searched for in the second file.
srcFile = file(srcFileName, 'r')

# This is the shorter file list that we are searching for matches in...
searchFile = file(searchFileName, 'r')

theDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S");

outFileName = "comparison-"+theDate+".csv"
outMissingFileName = "comparison-"+theDate+".missing.csv"
outErrorFileName = "comparison-"+theDate+".error.csv"

outFile = False
outMissingFile = False
outErrorFile = False

srcList = csv.reader(srcFile) #this is the longer list, it is read on the fly
masterList = list(csv.reader(searchFile)) #load into ram

# Columns as defined in the srcFile and searchFile CSVs.
typeCol = 0
hashCol = 1
pathCol = 2 # note paths should be formatted like the result of a "find ." command.

def getFilenamePath(fullPath):
    fileName,path = "",[]
    res = fullPath.split("/")

    if len(res) == 1:
        fileName = res[len(res)-1]
    elif len(res) > 1:
	fileName = res[len(res)-1]
	path = res

    return fileName,path

def getOutputRow(srcRowNum="", status="", matches="", identical="", type="", src="", des="" ):
    if srcRowNum == 0:
        return list( [ "Src#", "Type", "Matches", "Identical", "Status", srcFileName, searchFileName ] )
    elif srcRowNum == "summary":
        return list( [ "", "", "", "", "SUMMARY", status, "" ] )
    else:
        return list( [ str(srcRowNum), type, str(matches), str(identical), status, src, des ] )

def isNull(hash):
	return True if checkHash and hash == "d41d8cd98f00b204e9800998ecf8427e" else False

tot_row = 1
tot_identical = 0
tot_match = 0
tot_missing = 0
tot_null = 0
tot_recoverable = 0
tot_recover_maybe = 0
masterListCheckedOnce = False
out_header = False
outError_header = False
outMissing_header = False
headerRow = getOutputRow(0)
print(headerRow)

for srcRow in srcList:
	fileName,path = getFilenamePath(srcRow[pathCol])
	srcNull = isNull(srcRow[hashCol])
	cnt_null= 1 if srcNull else 0
	cnt_match = 0
	cnt_identical=0
	cnt_recoverable=0
	cnt_recover_maybe=0
	results = []

	for masterRow in masterList:

		masterNull = isNull(masterRow[hashCol])

		res = "MISSING"
		if srcNull and masterNull:
			res = "NULL"
			cnt_null = cnt_null if masterListCheckedOnce else cnt_null + 1
		elif checkHash and srcRow[typeCol] == "F" and srcRow[hashCol] and srcRow[hashCol] == masterRow[hashCol]:
			res = "HASH_MATCH"
			cnt_identical += 1
			cnt_match += 1

		if srcRow[pathCol] == masterRow[pathCol]:
			#path match
			if res == "HASH_MATCH":
				res = "IDENTICAL"
			elif srcNull != masterNull:
				cnt_recoverable += 1
				res = "RECOVERABLE"
			elif srcRow[typeCol] == "F":
				cnt_match += 1
				res = "CHANGED" if checkHash else "PATH_MATCH"
			else:
				cnt_match += 1
				res = "PATH_MATCH"
		elif (res != "NULL") or (srcNull and not masterNull and cnt_recoverable == 0):
			oFileName,oPath = getFilenamePath(masterRow[pathCol])

			if fileName == oFileName and srcRow[typeCol] != "D" and masterRow[typeCol] != "D": #srcRow[typeCol] == masterRow[typeCol]:
				#name match
				if res == "HASH_MATCH":
					res = "MOVED"
				elif srcNull != masterNull:
					res = "RECOVER_MAYBE"
					cnt_recover_maybe += 1
				else:
					res = "NAME_MATCH"

			elif res == "HASH_MATCH":
					res = "RENAMED"
		else:
			res = "SKIP"


		if res != "MISSING" and res != "SKIP" and res != "NULL":
			if (includeNameMatches) or (not includeNameMatches and res != "NAME_MATCH"):
				resData = [ tot_row, res, srcRow[typeCol], srcRow[pathCol], (masterRow[pathCol] if  res != "IDENTICAL" and res != "PATH_MATCH" else "") ]
				results.append(resData)


	masterListCheckedOnce = True
	tot_row += 1
	tot_match += cnt_match
	tot_identical += cnt_identical
	tot_null += cnt_null
	tot_recoverable += cnt_recoverable
	tot_recover_maybe += cnt_recover_maybe

	for r in results:
		if not outFile:
			outFile = file(outFileName, 'w')
			outWriter = csv.writer(outFile)
			outWriter.writerow( headerRow ) #populate header
		row = getOutputRow(r[0], r[1], cnt_match, cnt_identical, r[2], r[3], r[4])
		print(row)
		outWriter.writerow( row )

	if res == "NULL":
		if not outErrorFile:
			outErrorFile = file(outErrorFileName, 'w')
			outErrorWriter = csv.writer(outErrorFile)
			outErrorWriter.writerow( headerRow ) #populate header
		row = getOutputRow(tot_row, res, cnt_match, cnt_identical, srcRow[typeCol], srcRow[pathCol] )
		print(row)
		outErrorWriter.writerow ( row )
	elif cnt_match == 0:
		if not outMissingFile:
			outMissingFile = file(outMissingFileName, 'w')
			outMissingWriter = csv.writer(outMissingFile)
			outMissingWriter.writerow( headerRow ) #populate header
		row = getOutputRow(tot_row, res, cnt_match, cnt_identical, srcRow[typeCol], srcRow[pathCol] )
		print(row)
		outMissingWriter.writerow( row )


finalMsg = "TOTALS: Identical = "+str(tot_identical)+" Matches = "+str(tot_match)+" Missing = "+str(tot_row - tot_match)+" Null = "+str(tot_null)+" Recoverable = "+str(tot_recoverable)+" Recoverable Maybe = "+str(tot_recover_maybe)
print(finalMsg)
outWriter.writerow( getOutputRow("summary", finalMsg ) )

srcFile.close()
searchFile.close()

if outFile:
	outFile.close()
if outMissingFile:
	outMissingFile.close()
if outErrorFile:
	outErrorFile.close()
