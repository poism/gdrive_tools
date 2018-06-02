#!/bin/sh
#Po@poism.com
#This script was intended to output file list from Google FileStream (or any directory)
#It outputs into a csv sorted by path, with a column specifying if items are FOLDER or FILE..
#Due to a weird issue I was having with File Stream where directories didn't always load:
#If on the first run through of find . it results in folders not found, then
#it does a second pass on those specific folders at which point they usually are loaded.
#This perhaps would also be useful for autofs type systems?
#Final output files are .completelist.csv and .completelist.txt


theDate="`date +%Y%m%d_%H%M%S`"
thisDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "${1}" == "" ]; then
  echo "Arg missing: please pass a directory path to process!"
  exit
fi
if [ -d "${1}" ]; then
  inputDir="${1}" # the directory to process
else
  echo "Error: ${1} is not a directory!"
  exit
fi

inputDirName=`basename "${inputDir}"`
outputDir="${thisDir}/output/${inputDirName}"
baseName="${outputDir}/${inputDirName}_${theDate}"
fileList="${baseName}.list1.txt"
updatedList="${baseName}.list2.txt" #list from the folders that triggered errors first run through
errorList="${baseName}.errors.txt"
completeList="${baseName}.completelist.txt"
csv="${baseName}.completelist.csv"

mkdir -p "${outputDir}"

echo "input = ${inputDir}"
echo "output = ${outputDir}"
echo "fileList = ${fileList}"
echo "updatedList = ${updatedList}"
echo "errorList = ${errorList}"
echo "completeList = ${completeList}"

cd "$inputDir"

has_md5sum=0 # if this is a mac without md5sum, we can use md5 -r ....
if [ -x "$(command -v md5sum)" ]; then
	has_md5sum=1
fi

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
	if [ "${e}" == "." ]; then
		continue
	fi
  if [[ -f "${e}" ]]; then
	if [ "${has_md5sum}" == "1" ]; then
  		checksum=($(md5sum "${e}"))
	else
		# this is probably a mac so hopefully this will work:
  		checksum=($(md5 -r "${e}"))
	fi
    echo "F,${checksum},${e}" | tee -a "${csv}"
	elif [[ -d "${e}" ]]; then
    echo "D,'',${e}" | tee -a "${csv}"
	else
		echo "U,'',${e}" | tee -a "${csv}" #this wont happen
  fi

done < "${completeList}"
