#!/bin/bash

cd `dirname $0`


rm -fr install install.tar env.prepare

mkdir -p ./.clear
gocryptfs .enc .clear

rules=("-e s@__local_bin_dir__@../bin@")
while read STR; do
  if [[ -z "$STR" ]]; then
    continue
  fi

  name="__$(echo $STR | cut -f1 -d'=' | tr [:upper:] [:lower:])__"
  value=$(echo $STR | cut -f2 -d'=')

  rules+=("-e s@${name}@${value}@")
done < .clear/env.keys

cat env.template | sed ${rules[@]} > env.prepare

fusermount -u .clear


mkdir -p install/device/{bin,resources}
cp deps/bash/install/bin/bash install/device/bin/
cp deps/wget/install/bin/wget install/device/bin/
cp deps/mosquitto/install/bin/mosquitto_sub install/device/bin/
cp deps/mosquitto/install/bin/mosquitto_pub install/device/bin/
cp deps/jq/install/bin/jq install/device/bin/
cp deps/coreutils/install/bin/nohup install/device/bin/
cp deps/coreutils/install/bin/sleep install/device/bin/
cp deps/coreutils/install/bin/ls install/device/bin/
cp deps/coreutils/install/bin/base64 install/device/bin/
cp deps/coreutils/install/bin/nohup install/device/bin/
cp -a device/{src,prepare.sh,start.sh,stop.sh} install/device/
cp -a solver/clock_{words,digital,hands} install/device/resources/
cp env.prepare install/device/env.prepare


mkdir -p install/server/telegram
cp -a server/telegram/{src,prepare.sh,start.sh,stop.sh} install/server/telegram/
cp env.prepare install/server/telegram/env.prepare


mkdir -p install/server/main
cp -a server/main/{src,prepare.sh,start.sh,stop.sh} install/server/main/
cp -a server/main/resources install/server/main/resources
cp env.prepare install/server/main/env.prepare


tar -cf install.tar install/*
