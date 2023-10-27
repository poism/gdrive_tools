#!/bin/bash

echo 
echo "all: $@"
echo 

folder="${@: -1}"
args="${@:1}"

if [ "${folder}" = "${args}" ]; then
	echo
	echo "WARNING: No args given! If your folder names are perfect, you might want to cancel CTRL+C and prepend folder with arg: --keep-folder-name "
	echo "eg.. ./poism_folderBasedRename.py --keep-folder-name /path/to/A-Folder-Named-Exactly-How-I-Want-My-Files-To-Be-Named"
	echo
fi

echo "python poism_folderBasedRename.py ${args}"
python poism_folderBasedRename.py ${args}

./poism_webPrepImages.sh --docker ${folder}

if [ $? -eq 0 ]; then
	folder="${folder%/}"
	webfolder="${folder}/${folder##*/}_web"

	echo 
	echo "Processing finished, moving resized images to ${webfolder}"
	echo 
	
	mkdir ${webfolder}
	mv ${folder}/*_web.jpg ${webfolder}/
fi

echo 
echo "Done."
