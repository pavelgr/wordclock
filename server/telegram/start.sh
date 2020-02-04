#!/bin/bash

. docker.conf

docker run -d --restart always --name "${DOCKER_NAME}" "${DOCKER_IMAGE}"
