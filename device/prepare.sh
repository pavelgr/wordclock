#!/bin/bash

cd "$(dirname $0)"
#scriptDir="$(pwd)"


mqttHost="raspi3p"
mqttPort=1883

rules=()
rules+=("-e s@__mqtt_host__@${mqttHost}@")
rules+=("-e s@__mqtt_port__@${mqttPort}@")

cat env.prepare | sed "${rules[@]}" > .env


#sed -i -e "s:^#!/bin/bash:#!${scriptDir}/bin/bash:" src/wordclock.sh
