#! /bin/bash

if [ -z $1 ]; then
    echo "Emulates high jitter from remote host"
    echo "Usage $0 <REMOTE_HOST> <MINUMUM LATENCY> <JITTER>"
    echo ""
    echo "Example $0 192.168.1.1 500 200"
    exit 1
fi

remote_ip=$1
minimum_latency=$2
jitter=$3
interface="eth0"

tc qdisc add dev $interface root handle 1: prio
tc qdisc add dev $interface parent 1:3 handle 2: netem delay $(minimum_latency)ms $(jitter)ms 75%
tc filter add dev $interface protocol ip parent 1:0 prio 3 u32 match ip dst $remote_ip/32 flowid 1:3
