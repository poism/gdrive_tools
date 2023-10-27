#!/bin/bash

commit="$(git rev-parse --short HEAD)"
dirty="$( git diff --quiet || echo '-dirty' )"

tag="${commit}${dirty}"

docker build --tag poism/gdrivetools:${tag} .

docker tag poism/gdrivetools:${tag} poism/gdrivetools:latest
