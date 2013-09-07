#!/bin/bash

if [[ -z $1 ]] ; then
    echo "Usage: $0 path_to_map"
    exit 1
fi

python make_heightmap.py $1
pnmflip -tb $1/height.pnm | pnmtopng -compression 9 > $1/height.png
python tools/make_collisionmap.py < $1/height.pnm \
    | pnmtopng -compression 9 > $1/collision.png
