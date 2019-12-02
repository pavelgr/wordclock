#!/bin/bash

#ifdev=$(sudo ip route | grep default | sed -e 's/.*dev\ \([^ ]*\)\ .*/\1/')
#ifdevip=$(sudo ip -o -4 a | grep ${ifdev} | sed -e 's:.*[^0-9]\([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*\)/[0-9]*.*:\1:')

# STORAGE_HOST=${ifdevip}
# STORAGE_PORT=8000
#MQTT_HOST=${ifdevip}
# USER_UID=$(id -u ${USER})
# USER_GID=$(id -g ${USER})

# mkdir -p storage 1>/dev/null 2>&1

# docker run -d --restart always --name storage_server \
#     --read-only -v $(pwd)/storage:/storage \
#     -p ${ifdevip}:${STORAGE_PORT}:${STORAGE_PORT}/tcp \
#     python:3-slim-stretch /bin/bash -c "python -m http.server ${STORAGE_PORT} --directory /storage 1>/dev/null 2>&1"

docker run -d --restart always --name telegram_bot python:3-slim-stretch-telegram_bot

#    --env MQTT_HOST=${MQTT_HOST} \
