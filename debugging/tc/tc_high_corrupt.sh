#! /bin/bash

if [ -z $1 ]; then
    echo "Emulates corrupted packets from remote host"
    echo "Usage $0 <REMOTE_HOST> <CORRUPT_PERCENTAGE>"
    echo ""
    echo "Example $0 192.168.1.1 25"
    exit 1
fi

remote_ip=$1
corrupt_percentage=$2
interface="eth0"

tc qdisc add dev $interface root handle 1: prio
tc qdisc add dev $interface parent 1:3 handle 2: netem corrupt $corrupt_percentage%
tc filter add dev $interface protocol ip parent 1:0 prio 3 u32 match ip dst $remote_ip/32 flowid 1:3
