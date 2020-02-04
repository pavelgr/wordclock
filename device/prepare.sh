#!/bin/bash

cd "$(dirname $0)"
#scriptDir="$(pwd)"

cat env.prepare > .env

#sed -i -e "s:^#!/bin/bash:#!${scriptDir}/bin/bash:" src/wordclock.sh
