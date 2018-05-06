#!/bin/bash
if [ "${1}" == "" ]; then
	echo "Args missing! Requires path of folder to cleanup."
	exit
fi
targetDir="${1}"
thisDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
theDate="`date +%Y%m%d_%H%M%S`"
outputFile="${thisDir}/cleanup_${theDate}.log"

confirm () {
	echo "$1"
	read -p " y/n " response
	case "${response}" in
		[yY][eE][sS]|[yY])
			true
			;;
		*)
			false
			;;
	esac
}

cd "${targetDir}"
find . -iname "._*" -o -iname "__MACOSX" -o -iname ".DS_Store" -o -iname "Thumbs.db" -type f | tee -a "${outputFile}"

#find . -iname ".DS_Store" -type f -delete

if confirm "Review list of files to be deleted?  (y/n), press q to quit file view."; then
	less "${outputFile}"
fi
	
if confirm "Do you wish to delete all of these?"; then
	while read line; do
		echo "Deleting ${line}"
		rm "${line}"
	done <${outputFile}
fi

cd "${thisDir}"
