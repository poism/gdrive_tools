#!/bin/sh
#Po@poism.com
#This script was intended to output file list from Google FileStream
#If on the first run through of find . it results in folders not found
#it does a second pass by cd'ing directly into the folders that weren't found...
#This perhaps would also be useful for autofs type systems.

theDate="`date +%Y%m%d_%H%H%S`"
#PoismImagesNAS_inputDir="/home/poism/poismdisk2017/PoismGoogleBackup/FinalImages/"
#PoismImagesOLD_
inputDir="/home/poism/poismdisk2017/PoismGoogleBackup/PoismDrive/!PoismImages"
outputDir=/home/poism/poismdisk2017/DriveRecovery/
baseName=${outputDir}PoismImagesOLD_${theDate}
fileList=${baseName}.list1.txt
updatedList=${baseName}.list2.txt #list from the folders that triggered errors first run through
errorList=${baseName}.errors.txt
completeList=${baseName}.completelist.txt
csv=${baseName}.completelist.csv


echo "input = ${inputDir}"
echo "output = ${outputDir}"
echo "fileList = ${fileList}"
echo "updatedList = ${updatedList}"
echo "errorList = ${errorList}"
echo "completeList = ${completeList}"

cd "$inputDir"

find . > "${fileList}" 2> "${errorList}"

if [[ -f "${errorList}" ]]; then
        #on osx sed needs -i "" -e""
        sed -i '' -e 's/find: //g' "${errorList}"
        sed -i '' -e 's/:\ No\ such\ file\ or\ directory//g' "${errorList}"

        while read e
        do
                echo "$e"
                [ ! -d "${e}" ] && sleep 5
                #cd "$e"
                find "${e}" >> "${updatedList}"
                #cd ..
        done < "${errorList}"
fi

if [[ -f "${updatedList}" ]]; then
	cat "${updatedList}" >> "${fileList}"
fi

sort "${fileList}" > "${completeList}"

while read e
do
        if [[ -f "${e}" ]]; then
                echo "FILE,${e}" >> "${csv}"
	elif [[ -d "${e}" ]]; then
                echo "FOLDER,${e}" >> "${csv}"
	else
		echo "UNKNOWN,${e}" >> "${csv}"
        fi

done < "${completeList}"

