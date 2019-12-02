#!/bin/bash

INFO=1
VERBOSE=2
_V=${_V:-0}

scriptDir="$(dirname $0)"
envPath="${scriptDir}/../.env"

[[ -f ${envPath} ]] && {
    set -a
    . ${envPath}
    set +
}

controlPipeName="/tmp/wordclock_control"
storageImageDir="$(dirname $0)/${STORAGE_DIR}"
resourcesDir="$(dirname $0)/../resources"
localBinDir=""

[[ -z "${LOCAL_BIN_DIR}" ]] || {
    localBinDir="$(dirname $0)/${LOCAL_BIN_DIR}/"
}

childCount=0
childNames=()
childPids=()
childPipes=()

controlCount=0
controlNames=()
controlPids=()
controlPipe=""

defaultFeature="clock"
name="main"

exec {commonOut}>&1

trap quit SIGINT SIGKILL SIGTERM

I() {
    [[ $_V -ge $INFO ]] && { echo "I " $@ >&$commonOut; }
}

V() {
    [[ $_V -ge $VERBOSE ]] && { echo "V " $@ >&$commonOut; }
}

openPipe() {
    pipe=$1
    pipe=${pipe:-$(mktemp /tmp/temp.XXXXXX)}
    
    rm -fr $pipe
    mkfifo $pipe

    V "open pipe $pipe"

    echo $pipe
}

closePipe() {
    local pipe=$1

    [[ -z "$pipe" ]] || [[ -p "$pipe" ]] && {
        V "close pipe $pipe"

        rm $pipe 1>/dev/null 2>&1; 
    }
}

stopProcess() {
    local name=$1
    local process=$2

    [[ -z "$process" ]] || {
        V "stop $name: $process"

        kill -9 $process 1>/dev/null 2>&1; 
    }
}

makeSleep() {
    ${localBinDir}sleep $1
}

quit() {
    V "quit $name"

    local pids=$(ps --no-headers -o pid | xargs echo -n)
    local removePids=""
    local pid=$$

    while true; do
        local pidTmp=$(printf "%s\n" ${pids} | grep ${pid})
        [[ -z $pidTmp ]] && break

        removePids="$pidTmp ${removePids}"
    
        pid=$(ps --no-header -o ppid ${pid})
        [[ -z $pid ]] && break
    done

    local killPids=$(printf "%s\n" ${removePids} ${pids} | sort | uniq -u | xargs echo)
    V "kill subprocesses: ${killPids}"

    kill -SIGKILL ${killPids} >/dev/null 2>&1

    for i in ${!controlNames[@]}; do
        stopProcess ${controlNames[$i]} ${controlPids[$i]}
    done 
    closePipe $controlPipe

    for i in ${!childNames[@]}; do
        stopProcess ${childNames[$i]} ${childPids[$i]}
        closePipe ${childPipes[$i]}
    done

    exit 0
}

getFeatureIndex() {
    local feature=$1
    
    for i in ${!childNames[@]}; do
        if [[ "$feature" == "${childNames[$i]}" ]]; then
            echo $i

            return 0
        fi
    done
}

clock() {
    V "child $*"

    local name=$1
    local pipeIn=$2
    local process=""
    local storageImageDir="${storageImageDir}/${name}"

    local clockModes=(hands words digital)

    #trap quit SIGINT SIGKILL SIGTERM

    quit() {
        V "quit child $name"

        stopProcess $name $process
        
        exit 0
    }

    getClockMode() {
        local currentMode=$1
        local params=$2

        local indexUpdate=0
        case $params in
            hands|words|digital)
                currentMode=$params
                ;;
            next)
                indexUpdate=1
                ;;
            prev)
                indexUpdate=-1
                ;;
        esac

        local modeIndex=0
        for i in ${!clockModes[@]}; do
            if [[ "$currentMode" == "${clockModes[$i]}" ]]; then
                modeIndex=$i

                break
            fi
        done

        modeIndex=$(( $modeIndex + $indexUpdate ))
        if [[ $modeIndex -ge ${#clockModes[@]} ]]; then
            modeIndex=0
        elif [[ $modeIndex -lt 0 ]]; then
            modeIndex=$(( ${#clockModes[@]} - 1 ))
        fi

        echo "${clockModes[$modeIndex]}"
    }

    looper() {
        local currentMode="words"

        while true; do
            local command=""
            local params=""

            read command params < $pipeIn

            I "looper child $name: $command $params"
            
            case $command in
                start|resume|update)
                    stopProcess $name $process

                    if [[! -z "$params" ]]; then
                        currentMode=$(getClockMode "$currentMode" "$params")
                    fi

                    run &
                    
                    process=$!
                    prevParams=$params
                ;;
                stop|pause)
                    stopProcess $name $process
                ;;
                quit)
                    quit
                ;;
            esac
        done
    }
    
    getTime() {
        local minutes=$(printf "%02d" $(( 10#"$(date +'%M')" )) )
        local hour=$(printf "%02d" $(( 10#"$(date +'%H')" )) )

        echo "${hour}_${minutes}"
    }

    getPeriod() {
        local seconds=$(( 10#"$(date +'%S')" ))

        echo $(( 61 - $seconds ))
    }

    showClockImage() {
        [[ -z "$1" ]] || {
            V "showClockImage: $1"

            eips -g "$1" 1>/dev/null 2>&1
        }
    }

    run() {
        V "run child $name: $*"

        local time=$(getTime)

        local minutes=$(echo ${time} | cut -c4-5)
        if [[ "$minutes" == "00" ]]; then
            eips -c 1>/dev/null 2>&1
        fi
        
        showClockImage "${resourcesDir}/clock_${currentMode}/${time}.png"

        while true; do
            sleep $(getPeriod)

            showClockImage "${resourcesDir}/clock_${currentMode}/$(getTime).png"
        done
    }

    mkdir -p "${storageImageDir}" 1>/dev/null 2>&1

    looper

    V "exit child $name"
}

_image() {
    V "child $*"

    local name=$1
    local pipeIn=$2
    local process=""
    local storageImageDir="${storageImageDir}/${name}"

    #trap quit SIGINT SIGKILL SIGTERM

    quit() {
        V "quit child $name"

        stopProcess $name $process
        
        exit 0
    }

    looper() {
        local currentImage="clear"

        while true; do
            local command=""
            local params=""

            read command params < $pipeIn

            I "looper child $name: $command $params"
            
            case $command in
                start|resume|update)
                    stopProcess $name $process

                    if [[ ! -z "$params" ]]; then
                        currentImage=$(fetchImage $(_fetchImage "$currentImage" "$params") "$params")
                    fi

                    run &
                    
                    process=$!
                    prevParams=$params
                ;;
                stop|pause)
                    stopProcess $name $process
                ;;
                quit)
                    quit
                ;;
            esac
        done
    }

    _fetchImage() {
        local currentImage=$1
        local data=$2

        local imagePath="$currentImage"

        if [[ "$data" == "clear" || -f $data ]]; then
            imagePath="$data"

        elif [[ "$data" == base64://* ]]; then 
            data=${data:9}

            local imageName=$(echo "$data" | cut -c1-20 | md5sum - | cut -f1 -d' ')$(echo "$data" | cut -c1-4 | sed -e 's@/9j/@.jpg@; s@iVBO@.png@')
            if [[ ! -z "$imageName" ]] && [[ "$imageName" == *.png || "$imageName" == *.jpg ]]; then
                imagePath="${storageImageDir}/${imageName}"

                echo "$data" | ${localBinDir}base64 -d - > "${imagePath}"
            fi
        
        elif [[ "$data" == http://* ]]; then
            local imageName=$(basename "$data" 2>/dev/null)

            if [[ ! -z "$imageName" ]] && [[ "$imageName" == *.png || "$imageName" == *.jpg ]]; then
                imagePath="${storageImageDir}/${imageName}"
              
                ${localBinDir}wget "$data" -O "$imagePath" 1>/dev/null 2>&1
            fi
        fi

        echo "$imagePath"
    }

    run() {
        V "run child $name: $*"

        if [[ "$currentImage" == "clear" ]]; then
            return 0
        fi

        eips -g "$currentImage" 1>/dev/null 2>&1
    }

    mkdir -p "${storageImageDir}" 1>/dev/null 2>&1

    looper

    V "exit child $name"
}

image() {
    local cachedImages=( $(${localBinDir}ls -dt --sort=time "${storageImageDir}"/*) )
    V "$name: ${cachedImages[@]}"

    fetchImage() {
        local currentImage=$1
        local params=$2

        local imageIndex=-1
        for i in ${!cachedImages[@]}; do
            if [[ "$currentImage" == "${cachedImages[$i]}" ]]; then
                imageIndex=$i;

                break
            fi
        done

        if [[ $imageIndex -lt 0 ]]; then
            if [[ -f "$currentImage" ]]; then
                cachedImages+=( $currentImage )
            fi

            imageIndex=$(( ${#cachedImages[@]} - 1 ))
        fi

        case $params in
            prev|next)
                ;;
            *)
                echo "$currentImage"

                return 0
                ;;
        esac

        if [[ ${#cachedImages[@]} -eq 0 ]]; then
            echo "$currentImage"

            return 0
        fi

        local indexUpdate=0
        if [[ "$params" == "next" ]]; then
            indexUpdate=1
        elif [[ "$params" == "prev" ]]; then
            indexUpdate=-1
        fi

        imageIndex=$(( $imageIndex + $indexUpdate ))
        if [[ $imageIndex -ge ${#cachedImages[@]} ]]; then
            imageIndex=0
        elif [[ $imageIndex -lt 0 ]]; then
            imageIndex=$(( ${#cachedImages[@]} - 1 ))
        fi

        echo "${cachedImages[$imageIndex]}"
    }

    _image $@
}

weather() {
    fetchImage() {
        echo "$1"
    }

    _image $@
}

text() {
    fetchImage() {
        echo "$1"
    }

    _image $@
}

mqtt() {
    V "control $*"

    local name=$1
    local controlPipe=$2

    #trap quit SIGINT SIGKILL SIGTERM

    quit() {
        V "quit control $name"

        exit 0
    }

    run() {
        V "run control $name: $*"

        ${localBinDir}mosquitto_sub -h ${MQTT_HOST} -t ${MQTT_TOPIC_CONTROL} | while read json; do
            local feature=$(echo $json | ${localBinDir}jq -Mrc .type)
            local params=$(echo $json | ${localBinDir}jq -Mrc .value)

            I "control $name: $feature $params"

            echo "$name/$feature $params" > $controlPipe
        done
    }

    looper() {
        while true; do
            run
            makeSleep 5
        done
    }

    looper
}

buttons() {
    local BUTTON_RIGHT_NEXT=191
    local BUTTON_RIGHT_PREV=109
    local BUTTON_LEFT_NEXT=104
    local BUTTON_LEFT_PREV=193
    
    V "control $*"

    local name=$1
    local controlPipe=$2

    #trap quit SIGINT SIGKILL SIGTERM

    quit() {
        V "quit control $name"

        exit 0
    }

    getButton() {
        while true; do
            local key=$(/usr/bin/waitforkey | sed -e 's/[[:space:]]+/ /g')
            local code=$(echo ${key} | cut -f1 -d' ')
            local value=$(echo ${key} | cut -f2 -d' ')

            if [[ ${value} -ne 1 ]]; then
                continue
            fi

            V "getButton: key: ${code}"
            
            echo "${code}"
            break
        done
    }

    getNextFeature() {
        local key=$1
        local selectedFeature=$2

        featureIndex=$(getFeatureIndex $selectedFeature)
        if [[ ! -z "$featureIndex" ]]; then
            local indexUpdate=0
            case ${key} in
                ${BUTTON_RIGHT_NEXT})
                    indexUpdate=1
                    ;;
                ${BUTTON_RIGHT_PREV})
                    indexUpdate=-1
                    ;;
                ${BUTTON_LEFT_NEXT}|${BUTTON_LEFT_PREV})
                    indexUpdate=0
                    ;;
                *)
                    return 0
                    ;;
            esac

            featureIndex=$(( $featureIndex + $indexUpdate ))
            [[ $featureIndex -lt 0 ]] && {
                featureIndex=$(( $childCount - 1))
            }
            [[ $featureIndex -ge $childCount ]] && {
                featureIndex=0
            }

            echo "${childNames[$featureIndex]}"
        fi
    }

    getNextParams() {
        local key=$1
        local selectedFeature=$2

        case ${key} in
            ${BUTTON_LEFT_NEXT})
                echo "next"
                ;;
            ${BUTTON_LEFT_PREV})
                echo "prev"
                ;;
            *)
                ;;
        esac
    }

    run() {
        V "run control $name: $*"

        local selectedFeature=${defaultFeature}

        while true; do
            local key=$(getButton)

            local feature=$(getNextFeature ${key} ${selectedFeature})
            local params=$(getNextParams ${key} ${feature})

            [[ -z "$feature" ]] && { 
                continue
            }

            I "control $name: $feature $params"

            echo "$name/$feature $params" > $controlPipe

            selectedFeature=$feature
        done
    }

    looper() {
#        while true; do
            run
#            makeSleep 5
#        done
    }

    looper
}

manager() {
    V "manager $name"

    for f in clock image weather text; do
        pipe=$(openPipe)

        $f $f $pipe >&$commonOut 2>&1 &

        childPids+=( $! )
        childNames+=( $f )
        childPipes+=( $pipe )
        childCount=$(( $childCount + 1 ))
    done

    controlPipe=$(openPipe ${controlPipeName})
    for f in mqtt buttons; do
        $f $f $controlPipe >&$commonOut 2>&1 &

        controlPids+=( $! )
        controlNames+=( $f )
        controlCount=$(( $controlCount + 1 ))
    done

    I "child count: $childCount"
    for i in ${!childNames[@]}; do
        I "child ${childNames[$i]}: ${childPids[$i]} ${childPipes[$i]}"
    done

    I "control count: $controlCount"
    for i in ${!controlNames[@]}; do
        I "control ${controlNames[$i]}: ${controlPids[$i]} $controlPipe"
    done
}

request() {
    local feature=$1
    local params=$2

    local message=$(echo "$feature|$params" | ${localBinDir}jq -MRc 'split("|") | {type:.[0], value:.[1]}')

    ${localBinDir}mosquitto_pub -h ${MQTT_HOST} -p ${MQTT_PORT} -t ${MQTT_TOPIC_REQUEST} -m "$message" 1>/dev/null 2>&1
}

looper() {
    local selectedFeature="${defaultFeature}"

    for i in ${!childNames[@]}; do
        if [[ "$selectedFeature" == "${childNames[$i]}" ]]; then
            echo "start" > ${childPipes[$i]}

            break
        fi
    done

    while true; do
        local control=""
        local feature=""
        local params=""

        read feature params < $controlPipe

        I "looper $name: $feature $params"

        if [[ "$feature" == */* ]]; then 
            control=$(echo ${feature} | cut -f1 -d'/')
            feature=$(echo ${feature} | cut -f2 -d'/')
        fi

        if [[ "$feature" == "quit" ]]; then
            quit
        fi

        local featureIndex=$(getFeatureIndex $feature)
        if [[ -z "$featureIndex" ]]; then
            continue
        fi

        if [[ "$feature" == "weather" && "$control" != "mqtt" ]]; then
            request "$feature" "$params" &

            params="clear"
        fi

        if [[ "$selectedFeature" != "$feature" ]]; then
            eips -c 1>/dev/null 2>&1

            for i in ${!childNames[@]}; do
                if [[ $i -ne $featureIndex ]]; then
                    echo "pause" > ${childPipes[$i]}
                fi
            done

            makeSleep 0.1;

            echo "resume $params" > ${childPipes[$featureIndex]}; 
        
            selectedFeature="$feature"

        else 
            echo "update $params" > ${childPipes[$featureIndex]}; 
        fi
    done
}

mkdir -p "${storageImageDir}" 1>/dev/null 2>&1

manager
looper
