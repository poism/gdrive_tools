#!/bin/bash
#Sync Google Drive with Rclone
#Sync each root level folder individually in sets of 10.
#This is assuming each root level folder might be huge and that there may be errors...


rcloneremote=poismdrive
synctarget="./backup"
tmpdir="./tmp"
thedate="`date +%Y%m%d`" #_%H%M%S`"
basename="${rcloneremote}_${thedate}"
infile="${tmpdir}/${basename}.txt"
outfile="${tmpdir}/${basename}_foldersOnly.txt"
splitbasename="${tmpdir}/${basename}_split_"

mkdir -p "${tmpdir}"

main_menu() {
	PS3='Select option: '
	options=( "Quit" "List Directories" "Cleanup List" "Start Backup")
	select opt in "${options[@]}"
	do
	case $opt in
	"List Directories")
		rclone lsd $rcloneremote:/ > $infile
		less $infile
		main_menu
	;;
	"Cleanup List")
		while read l; do
			echo "${l##*-1 }" >> $outfile
		done <$infile
		split -l 10 $outfile $splitbasename
		ls ${splitbasename}*
		main_menu
	;;
	"Start Backup")
		for filename in ${splitbasename}*; do
			while read d; do
				target="${synctarget}/${d}"
				echo "------------------ Backing up ${d} ------------------"
				mkdir -p "${target}"
				rclone sync "${rcloneremote}:/${d}" "${target}"
			done<${filename}
		done
		main_menu
	;;
	"Quit")
		exit 0
	;;
	*)
		exit 0
	;;
	esac
	done
}

main_menu

