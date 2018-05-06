import csv
import string

# This script is intended to compare two csv outputs from poism_getFolderFileList.sh
# This will output a final csv that shows all missing files.

f1Name = 'Compared_Nas-and-DB_20171119_OldOnly.csv'
f1 = file(f1Name, 'r')
f2Name = 'PoismImagesNAS-and-DB_20171119.completelists.csv'
f2 = file(f2Name, 'r')
f3 = file('PYCOMPARE_20171119_PoismImagesNAS-and-DB_Compared_Nas-and-DB_OldOnly.csv', 'w')
f4 = file('PYCOMPARE_20171119_PoismImagesNAS-and-DB_Compared_Nas-and-DB_OldOnly-MISSING.csv', 'w')

srcList = csv.reader(f1)
masterList = list(csv.reader(f2)) #loading into ram
outFiles = csv.writer(f3)
outMissing = csv.writer(f4)


# columns:
# 0 = "FullPath",

includedCols = [ 0 ]

def getFilenamePath(fullPath):
    fileName,path = "",[]
    res = fullPath.split("/")

    if len(res) == 1:
        fileName = res[len(res)-1]
    elif len(res) > 1:
	fileName = res[len(res)-1]
	path = res

    return fileName,path



r = 1
cnt0=0 #identical
cnt1=0 #found
cnt2=0 #not found

outFiles.writerow( [ "0", "Status", "Found", f1Name, f2Name ] )

for srcRow in srcList:
	fileName,path = getFilenamePath(srcRow[0])
	resRow = list( str(r) )
	missing = True
	for masterRow in masterList:
		# result columns: 0:srcRowNum, 1:status, 2: src, 3: des
		found = 0
		if masterRow[0] == srcRow[0]:
			cnt0 = cnt0+1
			found = found+1
			res = "IDENTICAL"
		else:
			oFileName,oPath = getFilenamePath(masterRow[0])

			if fileName == oFileName:
				cnt1 = cnt1+1
				found = found+1
				res = "FOUND"
			else:
				cnt2 = cnt2+1
				res = "MISSING"

		if res != "MISSING":
			missing = False
			resRow = list( [str(r), str(found), res, srcRow[0], masterRow[0] ] )
			print(resRow)
			outFiles.writerow(resRow)

	if missing == True:
		outMissing.writerow( [str(r), str(found), res, srcRow[0] ] )

	r = r + 1

finalMsg = "Count: Identical = "+str(cnt0)+", Found = "+str(cnt1)+", Missing = "+str(cnt2)
print(finalMsg)
outFiles.writerow( [ "!", "!", "SUMMARY", finalMsg ] )

f1.close()
f2.close()
f3.close()
