#! /bin/bash

if [ -z $1 ]; then
    echo "Emulates closing connection from remote side"
    echo "Usage $0 <PID> <HOST:PORT>"
    echo ""
    echo "Example $0 12345 192.168.1.1:6379"
    echo "Example $0 12345 6379"
    exit 1
fi

PID=$1
HOSTPORT=$2

FDS=`nsenter -t $PID -n lsof -n -p $PID | grep ESTABLISHED | grep "$HOSTPORT" | awk '{print $4}' | sed 's/[^0-9]//g'`

if [ ! -z "$FDS" ]; then
    for fd in $FDS
    do
        gdb --batch-silent -p $PID -ex "call (int) shutdown($fd, 0)" -ex detach -ex quit
    done
else
    echo "fd not found"
fi
