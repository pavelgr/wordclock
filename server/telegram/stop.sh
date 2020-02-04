#!/bin/bash

. docker.conf

containers=$(docker container ls -a | sed -E -e 's/[[:space:]]+/ /g')

cids=""
for f in "${DOCKER_IMAGE}"; do
    cids="$cids $(echo "${containers}" | grep ${f} | cut -f1 -d' ')"
done

docker container stop ${cids}
