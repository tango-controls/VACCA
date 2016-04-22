#!/bin/sh

echo "mydevice.sh DEVICE INSTANCE LOGS"

DEVICE=$1
INSTANCE=$2
LOGS=$3

cd /home/srubio/PROJECTS/DeviceServers
screen $DEVICE/src/$DEVICE.py $INSTANCE $LOGS

