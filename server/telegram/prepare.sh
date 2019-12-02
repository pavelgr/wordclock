#!/bin/bash

docker image rm python:3-slim-stretch-telegram_bot


mqttHost=$(hostname)
mqttPort=1883

rules=()
rules+=("-e s@__mqtt_host__@${mqttHost}@")
rules+=("-e s@__mqtt_port__@${mqttPort}@")

cat env.prepare | sed "${rules[@]}" > .env


docker build -t python:3-slim-stretch-telegram_bot -f- . <<EOF
FROM python:3-slim-stretch

RUN apt-get update && apt-get -y install gcc libffi-dev libssl-dev zlib1g-dev libjpeg-dev libfreetype6-dev && apt-get clean
RUN pip install python-dotenv paho-mqtt python-telegram-bot

ADD src /application/src/
COPY .env /application/.env

RUN useradd -ms /bin/bash tmpuser
RUN chown -R tmpuser:tmpuser /application

USER tmpuser

CMD [ "/usr/local/bin/python", "/application/src/bot.py"]
EOF

#RUN echo '#!/bin/bash \n\
#cat /application/env.prepare | sed -e "s@__mqtt_host__@\${MQTT_HOST}@;" > /application/.env \n\
#python /application/src/bot.py \n\
#' > /application/run.sh

#RUN groupadd -r -g ${gid} ${USER} && useradd -r -u ${uid} -g ${gid} ${USER}

# RUN echo '#!/bin/bash \n\
# [[ -f /application/.user ]] || { groupadd -r -g \${USER_GID} \${USER}; useradd -r -u \${USER_UID} -g \${USER_GID} ${USER}; touch /application/.user; } \n\
# chown -R \${USER}:\${USER} /application/storage \n\
# cat /application/env.prepare | sed -e "s@__mqtt_host__@\${MQTT_HOST}@; s@__storage_host__@\${STORAGE_HOST}@; s@__storage_port__@\${STORAGE_PORT}@" > /application/.env \n\
# exec sudo -u \${USER} -g \${USER} -- python /application/src/bot.py \n\
# ' > /application/run.sh

#USER ${USER}:${USER}
#ENTRYPOINT ["/bin/bash", "/application/entrypoint.sh"]
