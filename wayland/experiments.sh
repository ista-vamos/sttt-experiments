#!/bin/bash

xauth add $XAUTH\
	|| echo "xauth failed, if there are problems with running X, call 'xhost +' from your system (not from the docker)"

CSV=results.csv
mkdir -p logs

DEV=$(echo "-1"  | evemu-describe 2>&1 | grep -i 'touchpad' | cut -d ':' -f 1)
if [ ! -c "$DEV" ]; then
	echo -e "Failed detecting the touchpad device"
	echo -e "Please set the variable DEV in $0 manually\n"
	echo -e "E.g., DEV=/dev/input/event13\n"
	echo -e "The list of devices can be obtained via 'evemu-describe' or 'libinput list-devices'"
	exit 1
fi

if [ -z "$DEVTYPE" ]; then
	echo "Set DEVTYPE to either 'touchpad' or 'mouse'"
	exit 1
fi

for BUFSIZE in 3; do
for TAU in 10 30 50; do
for DELTA in 10 30 50 70 100; do
for EVENTS in $DEVTYPE-events*.txt; do
	make BUFSIZE=$BUFSIZE TAU=$TAU DELTA=$DELTA
	rm monitor.log
	./run.sh $EVENTS $DEV
	cp monitor.log logs/$EVENTS-$BUFSIZE-$TAU-$DELTA-monitor.log

	NUMS=$(python parse_log.py monitor.log)
	echo -e "\e[0;31m$EVENTS,$BUFSIZE,$TAU,$DELTA,$NUMS\e[0m"
	echo "$EVENTS,$BUFSIZE,$TAU,$DELTA,$NUMS" >> $CSV
done
done
done
done
