import csv, string, datetime

# This script is intended to compare two csv outputs from poism_getFolderFileList.sh
# This will output a final csv that shows items all missing files, or duplicate file names in multiple locations, etc.
# Note, files existing in searchFile but not existing in srcFile are currently completely ignored... it's a one way verification.
# For instance, use this to compare a current folder structure with an old backup of the same hierarchy... or to check data migration.
# Can for static backups, can also be checked against old completelist.csv to detect bitrot.

theDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S");

srcFileName = 'src.completelist.csv' # This MUST be the LONGER filelist csv! Each line in this file will be searched for in the second file.
srcFile = file(srcFileName, 'r')

searchFileName = 'search.completelist.csv' # This is the shorter file list that we are searching for matches in...
searchFile = file(searchFileName, 'r')

outFileName = "comparison-"+theDate+".csv"
outFile = file(outFileName, 'w')

outMissingFileName = "comparison-"+theDate+".missing.csv"
outMissingFile = file(outMissingFileName, 'w')

srcList = csv.reader(srcFile) #this is the longer list, it is read on the fly
masterList = list(csv.reader(searchFile)) #load into ram
outWriter = csv.writer(outFile)
outMissingWriter = csv.writer(outMissingFile)

checkHash = True
includeNameMatches = False

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

tot_row = 1
tot_identical = 0
tot_match = 0
tot_missing = 0

headerRow = getOutputRow(0)
print(headerRow)
outWriter.writerow( headerRow ) #populate header
outMissingWriter.writerow( headerRow ) #populate header

for srcRow in srcList:
	fileName,path = getFilenamePath(srcRow[pathCol])
	cnt_match = 0
	cnt_identical=0
	results = []
	for masterRow in masterList:
		res = "MISSING"
		if checkHash and srcRow[typeCol] == "F" and srcRow[hashCol] and srcRow[hashCol] == masterRow[hashCol]:
			res = "HASH_MATCH"
			cnt_identical += 1
			cnt_match += 1

		if srcRow[pathCol] == masterRow[pathCol]:
			#path match
			if res == "HASH_MATCH":
				res = "IDENTICAL"
			elif srcRow[typeCol] == "F":
				cnt_match += 1
				res = "CHANGED" if checkHash else "PATH_MATCH"
			else:
				#matched paths do not count, only matched files
				res = "PATH_MATCH"
		else:
			oFileName,oPath = getFilenamePath(masterRow[pathCol])

			if fileName == oFileName and srcRow[typeCol] == masterRow[typeCol]:
				#name match
				if res == "HASH_MATCH":
					res = "MOVED"
				else:
					res = "NAME_MATCH"

			elif res == "HASH_MATCH":
					res = "RENAMED"

		if res != "MISSING":
			if (includeNameMatches) or (not includeNameMatches and res != "NAME_MATCH"):
				resData = [ tot_row, res, srcRow[typeCol], srcRow[pathCol], masterRow[pathCol] ]
				results.append(resData)

	tot_row += 1
	tot_match += cnt_match
	tot_identical += cnt_identical

	if cnt_match == 0:
		row = getOutputRow(tot_row, res, cnt_match, cnt_identical, srcRow[typeCol], srcRow[pathCol] )
		print(row)
		outMissingWriter.writerow( row )
	else:
		for r in results:
			row = getOutputRow(r[0], r[1], cnt_match, cnt_identical, r[2], r[3], r[4])
			print(row)
			outWriter.writerow( row )


finalMsg = "TOTALS: Identical = "+str(tot_identical)+" Matches = "+str(tot_match)+" Missing = "+str(tot_row - tot_match)
print(finalMsg)
outWriter.writerow( getOutputRow("summary", finalMsg ) )

srcFile.close()
searchFile.close()
outFile.close()
outMissingFile.close()
