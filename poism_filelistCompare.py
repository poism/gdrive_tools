import csv, string, datetime

# This script is intended to compare two csv outputs from poism_getFolderFileList.sh
# This will output a final csv that shows all missing files, or duplicate file names in multiple locations, etc.
# For instance, use this to compare a current folder structure with an old backup of the same hierarchy... or to ensure migration was successful.

theDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S");

srcFileName = 'src.completelists.csv' # This MUST be the LONGER filelist csv! Each line in this file will be searched for in the second file.
srcFile = file(srcFileName, 'r')

searchFileName = 'search.completelists.csv' # This is the shorter file list that we are searching for matches in...
searchFile = file(searchFileName, 'r')

outFileName = "comparison-"+theDate+".csv"
outFile = file(outFileName, 'w')

outMissingFileName = "comparison-"+theDate+"-MISSING.csv"
outMissingFile = file(outMissingFileName, 'w')

srcList = csv.reader(srcFile) #this is the longer list, it is read on the fly
masterList = list(csv.reader(searchFile)) #load into ram
outWriter = csv.writer(outFile)
outMissingWriter = csv.writer(outMissingFile)

# Columns as defined in the srcFile and searchFile CSVs.
typeCol = 0
pathCol = 1 # note paths should be formatted like the result of a "find ." command.

def getFilenamePath(fullPath):
    fileName,path = "",[]
    res = fullPath.split("/")

    if len(res) == 1:
        fileName = res[len(res)-1]
    elif len(res) > 1:
	fileName = res[len(res)-1]
	path = res

    return fileName,path

def getOutputRow(srcRowNum="", status="", matches="", type="", src="", des="" ):
    if srcRowNum == 0:
        return list("0", "SrcRowNum", "Status", "Matches", "Type", srcFileName, searchFileName)
    elif srcRowNum == "summary":
        return list("", "", "", "", "SUMMARY", "status", "" )
    else:
        return list( [str(srcRowNum), status, str(matches), type, src, des] )

r = 1
cnt0=0 #identical
cnt1=0 #found
cnt2=0 #not found

outWriter.writerow( getOutputRow(0) )

for srcRow in srcList:
	fileName,path = getFilenamePath(srcRow[pathCol])
	missing = True
	for masterRow in masterList:
		found = 0
		if masterRow[srcPathCol] == srcRow[pathCol]:
			cnt0 = cnt0+1
			found = found+1
			res = "IDENTICAL"
		else:
			oFileName,oPath = getFilenamePath(masterRow[pathCol])

			if fileName == oFileName and srcRow[typeCol] == masterRow[typeCol]:
				cnt1 = cnt1+1
				found = found+1
				res = "FOUND"
			else:
				cnt2 = cnt2+1
				res = "MISSING"

		if res != "MISSING":
			missing = False
			resRow = getOutputRow(r, res, found, srcRow[pathCol], srcRow[pathCol], masterRow[pathCol] )
			print(resRow)
			outWriter.writerow(resRow)

	if missing == True:
		outMissingWriter.writerow( getOutputRow(r, res, found, srcRow[pathCol] ) )

	r = r + 1

finalMsg = "Count: Identical = "+str(cnt0)+", Found = "+str(cnt1)+", Missing = "+str(cnt2)
print(finalMsg)
outWriter.writerow( getOutputRow("summary", finalMsg ) )

srcFile.close()
searchFile.close()
outFile.close()
outMissingFile.close()
