#!/bin/bash

containers=$(docker container ls -a | sed -E -e 's/[[:space:]]+/ /g')

cids=""
for f in main; do
    cids="$cids $(echo "${containers}" | grep ${f} | cut -f1 -d' ')"
done

docker container stop ${cids}
