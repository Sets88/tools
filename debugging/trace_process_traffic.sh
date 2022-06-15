#! /bin/sh

help() {
    echo -e "Trace data exchange\nUsage:\n $0 {PID} {PORT}"
}

if [ -z "$2" ]; then
    help
    exit 1
fi

if [ -z "$1" ]; then
    help
    exit 1
fi

PID=$1
PORT=$2

#SYSCALLS="read,write,recvfrom,sendto"
SYSCALLS="all"
# Print all process connections
nsenter -t $PID -n lsof -i -a -n -P -p $PID

# Find all file descriptors related to connections you want to monitor
FDS=`nsenter -t $PID -n lsof -i -a -n -P -p $PID | grep ":${PORT}\(->\| (ESTABLISHED)\)" | awk 'ORS="\\\|" {sub("[^[:digit:]]+", "", $4); print $4}' | head --bytes -2`

if [ -z "$FDS" ]; then
    echo "Current process doesn't have connections related to port ${PORT}"
    exit 1
fi

echo FDS: $FDS

nsenter -t $PID -n strace -f -p $PID -e $SYSCALLS -s 10000 2>&1 | grep "^\[pid *[0-9]*\] *[0-9a-zA-Z\-\_]*(\(${FDS}\),"
