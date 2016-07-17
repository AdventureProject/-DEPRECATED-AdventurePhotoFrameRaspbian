#!/bin/bash
STATE=`cat /sys/class/net/wlan0/operstate`

if [ "$STATE" = "up" ] ; then
	echo "0"
	exit 0;
else
	echo "1"
	exit 1;
fi
