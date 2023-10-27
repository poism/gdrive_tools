#!/bin/bash

if [ -z "${1}" ]; then
	echo "error no args given"
	exit 1
fi

folder="${@: -1}"
args="${@:1}"

echo
echo "folder: $folder"
echo "args: $args"
echo

uid=`id -u`
gid=`id -g`
 

echo "docker run -it --rm --name gdrivetools \ "
echo "	--user ${uid}:${gid} \ "
echo "	-v ${folder}:${folder} \ "
echo "	-v $PWD:/opt/poism/app \ "
echo "	-w /opt/poism/app poism/gdrivetools:latest \ "
echo "	/bin/bash docker-entrypoint.sh ${args}"

docker run -it --rm --name gdrivetools \
	--user ${uid}:${gid} \
	-v "${folder}":"${folder}" \
	-v "$PWD":/opt/poism/app \
	-w /opt/poism/app poism/gdrivetools:latest \
	/bin/bash docker-entrypoint.sh ${args}

