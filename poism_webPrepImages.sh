#!/bin/bash
# Po@poism.com
# Pass this script a directory and it will convert all png,bmp,tif,tga,jpg to 1920x1080px equivalent jpg's under 1300kb

if [ -z "${1}" ]; then
	echo "No directory given to explore! Exiting."
	exit
fi
initialDir="`pwd`"
cd "${1}"

# Remote hidden junk
rm ._*

# Make names consistent
find . -maxdepth 1 -type f -name '.JPEG' -o -name '.jpeg' -o -name '.JPG' -print0 | while IFS= read -r -d $'\0' file_name; do mv "${file_name}" "${file_name%.}.jpg"; done

find . -maxdepth 1 -type f -name '.PNG' -print0 | while IFS= read -r -d $'\0' file_name; do mv "${file_name}" "${file_name%.}.png"; done

find . -maxdepth 1 -type f -name '.BMP' -print0 | while IFS= read -r -d $'\0' file_name; do mv "${file_name}" "${file_name%.}.bmp"; done

find . -maxdepth 1 -type f -name '.TIF' -print0 | while IFS= read -r -d $'\0' file_name; do mv "${file_name}" "${file_name%.}.tif"; done

find . -maxdepth 1 -type f -name '.TGA' -print0 | while IFS= read -r -d $'\0' file_name; do mv "${file_name}" "${file_name%.}.tga"; done


# Reduce images larger than 1300kb to 90 quality jpgs, 1920x1080 px equivalent resolution.
find . -maxdepth 1 -name "*.jpg" -size +1300k -exec convert -quality 90 -resize '2073600@' "{}" "{}" \;

# Reduce images smaller than 1300kb at estimated equivalent quality, only if higher than 1920x1080 px equivalent resolution.
find . -maxdepth 1 -name "*.jpg" -size -1300k -exec convert -resize '2073600@>' "{}" "{}" \;

# Reduce images larger than 1300kb to 90 quality jpgs, 1920x1080 px equivalent resolution.
find . -maxdepth 1 -name "*.jpg" -size +1300k -exec convert -quality 90 -resize '2073600@' "{}" "{}" \;

# Convert non-jpgs to 90 quality jpg, resize if greater than 1920x1080px equivalent resolution.
if [ "$(ls -A *.png)" ]; then
	for img in *.png; do convert -quality 90 -resize '2073600@>' "${img}" "${img%.}.jpg"; done
fi
if [ "$(ls -A *.bmp)" ]; then
	for img in *.bmp; do convert -quality 90 -resize '2073600@>' "${img}" "${img%.}.jpg"; done
fi
if [ "$(ls -A *.tga)" ]; then
	for img in *.tga; do convert -quality 90 -resize '2073600@>' "${img}" "${img%.}.jpg"; done
fi
if [ "$(ls -A *.tif)" ]; then
	for img in *.tif; do convert -quality 90 -resize '2073600@>' "${img}" "${img%.}.jpg"; done
fi

echo "Done."

cd "${initialDir}"

