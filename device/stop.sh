#!/bin/sh

killCmdName="wordclock"

#mySession=$(ps --no-headers -o sid | sort | uniq)
myPids=$(ps --no-headers -o pid)

killSessions=$(ps --no-headers -A -o sid,pid,cmd | grep "${killCmdName}" | sed -e "s/^[ ]*//" | cut -f1 -d' ' | sort | uniq)
#killSessions=$(sort ${mySession} ${otherSessions} | uniq -u)

otherPids=""
for f in $(echo ${killSessions}); do
    otherPids="${otherPids} $(ps --no-headers -o pid -s ${f})"
done

killPids=$(printf "%s\n" ${myPids} ${otherPids} | sort | uniq -u)

[[ -z "${killPids}" ]] || {
    kill -SIGTERM ${killPids} 1>/dev/null 2>&1
    
    sleep 2

    kill -SIGKILL ${killPids} 1>/dev/null 2>&1
}
