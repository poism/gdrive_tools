#!/bin/bash
# Po@poism.com
# Pass this script a directory and it will convert all png,bmp,tif,tga,jpg to 1920x1080px equivalent jpg's under 1300kb

thisDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
theDate="`date +%Y%m%d_%H%M%S`"
initialDir="`pwd`"
recursive="false"
resizedString="" #appended before extension of resized files, eg. _resized
quality=65
docker=0
#960000 = 1200x800
#1440000 = 1600x900
#1024000 = 1280x800
#stripString="-strip -profile ${thisDir}/sRGB2014.icc "
stripString=""

if [ "${1}" == "--docker" ]; then
	docker=1
	targetDir="${2}"

elif [ "${1}" == "--recursive" ]; then
		echo "RECURSIVE MODE ENABLED!"
		recursive="true"
		if [ -z "${2}" ]; then
			echo "No directory given to explore! Exiting."
			exit 2
		else
			targetDir="${2}"
		fi
elif [ -z "${1}" ]; then
	echo "No directory given to explore! Exiting."
	exit 2
else
	targetDir="${1}"
fi

function cleanupJunk() {
	# Remote hidden junk
	echo "Removing junk files. ( ._* , __MACOSX , .DS_Store , Thumbs.db )"
	find . -maxdepth 1 -type f \( -iname "._*" -o -iname "__MACOSX" -o -iname ".DS_Store" -o -iname "Thumbs.db" \) -exec rm "{}" \;
}

function makeNamesConsistent() {
	# Make names consistent
	echo "Making image names consistent."
	find . -maxdepth 1 -type f \( -name "*.JPEG" -o -name "*.jpeg" -o -name "*.JPG" \) -print0 | while IFS= read -r -d $'\0' img; do mv "${img}" "${img%.*}.jpg"; done
	find . -maxdepth 1 -type f -name "*.PNG" -print0 | while IFS= read -r -d $'\0' img; do mv "${img}" "${img%.*}.png"; done
	find . -maxdepth 1 -type f -name "*.BMP" -print0 | while IFS= read -r -d $'\0' img; do mv "${img}" "${img%.*}.bmp"; done
	find . -maxdepth 1 -type f -name "*.TIF" -print0 | while IFS= read -r -d $'\0' img; do mv "${img}" "${img%.*}.tif"; done
	find . -maxdepth 1 -type f -name "*.TGA" -print0 | while IFS= read -r -d $'\0' img; do mv "${img}" "${img%.*}.tga"; done
}

function resizeJpg() {
	echo "Resizing JPGs"
	# Reduce images smaller than 1300kb at estimated equivalent quality, only if higher than 1920x1080 px equivalent resolution.
	find . -maxdepth 1 -name "*.jpg" -size -500k -print0 | while IFS= read -r -d $'\0' img; do
		#convert -colorspace sRGB -background black -resize '1440000@>' "${img}" "${img%.*}${resizedString}.jpg"
		#convert -colorspace sRGB ${stripString}-background black -resize '960000@>' "${img}" "${img%.*}${resizedString}.jpg"
		convert -colorspace sRGB ${stripString}-background black -resize '2160000@>' "${img}" "${img%.*}${resizedString}.jpg"
	done

	# Reduce images larger than 1300kb to 90 quality jpgs, 1920x1080 px equivalent resolution.
	find . -maxdepth 1 -name "*.jpg" -size +500k -print0 | while IFS= read -r -d $'\0' img; do
		#convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '960000@' "${img}" "${img%.*}${resizedString}.jpg"
		convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '2160000@' "${img}" "${img%.*}${resizedString}.jpg"
	done
}

function convertToJpg() {
	echo "Converting .png, .bmp, .tga, .tif to .jpg"
	# Convert non-jpgs to 90 quality jpg, resize if greater than 1920x1080px equivalent resolution.
	if [ "$(ls -A *.png)" ]; then
		for img in *.png; do
			#convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '786432@<' -resize '1440000@>' "${img}" "${img%.*}${resizedString}.jpg"
			#convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '960000@>' "${img}" "${img%.*}${resizedString}.jpg"
			convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '2160000@>' "${img}" "${img%.*}${resizedString}.jpg"
			[[ "${resizedString}" == "" ]] && rm "${img}"
		done
	fi
	if [ "$(ls -A *.bmp)" ]; then
		for img in *.bmp; do
			#convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '960000@>' "${img}" "${img%.*}${resizedString}.jpg"
			convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '2160000@>' "${img}" "${img%.*}${resizedString}.jpg"
			[[ "${resizedString}" == "" ]] && rm "${img}"
		done
	fi
	if [ "$(ls -A *.tga)" ]; then
		for img in *.tga; do
			#convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '960000@>' "${img}" "${img%.*}${resizedString}.jpg"
			convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '2160000@>' "${img}" "${img%.*}${resizedString}.jpg"
			[[ "${resizedString}" == "" ]] && rm "${img}"
		done
	fi
	if [ "$(ls -A *.tif)" ]; then
		for img in *.tif; do
			#convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '960000@>' "${img}" "${img%.*}${resizedString}.jpg"
			convert -colorspace sRGB ${stripString}-background black -quality ${quality} -resize '2160000@>' "${img}" "${img%.*}${resizedString}.jpg"
			[[ "${resizedString}" == "" ]] && rm "${img}"
		done
	fi
}

function processFolder() {
	echo "=============================="
	echo "Directory: ${1}"
	echo "------------------------------"
	cd "${1}"
	echo "=========== BEFORE ==========="
	#ls -alSh
	find . -maxdepth 1 -type f -exec du -h {} + | sort -h
	du -hcs "`pwd`"

	echo "------------------------------"
	cleanupJunk
	echo "------------------------------"
	makeNamesConsistent
	echo "------------------------------"
	resizeJpg
	echo "------------------------------"
	convertToJpg

	echo "=========== AFTER ==========="
	#ls -alSh
	find . -maxdepth 1 -type f -exec du -h {} + | sort -h
	du -hcs "`pwd`"

	echo "=========== DONE ============"
	if [ "${recursive}" == "true" ]; then
		for f in *; do
			if [[ -d "${f}" ]]; then
				processFolder "${f}"
			fi
		done
	fi
}

#cd "${1}"

if [[ ${docker} -eq 1 ]] && [[ -d "${targetDir}" ]]; then
	resizedString="_web"
	echo "DOCKER MODE"
	echo "Your resizedString is: ${resizedString} , resulting files will look like: thefilename${resizedString}.jpg"
	read -r -p "Shall we proceed? [y/N]" response
	case "$response" in
		[yY][eE][sS]|[yY])
			processFolder "${targetDir}"
			;;
		*)
			echo "Exiting..."
			exit 1
		;;
	esac
elif [[ -d "${targetDir}" ]]; then
	echo "WARNING: This will alter all of the files in the ${targetDir} directory."
	echo "Do you wish to make a backup first? ( ${targetDir%/}_backup )"
	read -r -p "Backup? [y/N] " response
	case "$response" in
		[yY][eE][sS]|[yY])
			echo "Backing up to ${targetDir%/}"
			cp -rv "${targetDir}" "${targetDir%/}_backup"
			;;
		*)
			echo "Not backing up..."
		;;
	esac
	echo "WARNING: Currently we will replace the original files when resizing!"
	echo "(and we will delete the originals if they were non JPG format after converting them!)"
	echo "If you wish to retain the originals, please give a short string to append to filenames of the resized versions."
	echo " eg. _resized , or _web"
	echo "Just leave it empty and press ENTER if you want an empty string (thus replacing original files!)"
	read -r -p "Enter your resizedString, or leave empty to replace originals:" resizedString
	echo "Your resizedString is: ${resizedString} , resulting files will look like: thefilename${resizedString}.jpg"
	read -r -p "Shall we proceed? [y/N]" response
	case "$response" in
		[yY][eE][sS]|[yY])
			processFolder "${targetDir}"
			;;
		*)
			echo "Exiting..."
			exit 0
		;;
	esac

else
	echo "Error: ${targetDir} is NOT a directory!"
	exit 2
fi


echo "Done."
cd "${initialDir}"
