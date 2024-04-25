#!/bin/bash

set -e

cd $(dirname $0)
source ../setup-vars.sh

if [ ! -f "$1" ]; then
	echo "First argument is the file with events"
	exit 1
fi

if [ ! -c "$2" ]; then
	echo "Second argument is the touchpad/mouse device, e.g., /dev/input/event11"
	echo "Here's a list of devices that you probably want:"
	echo "-1" | evemu-describe 2>&1 | grep -Ei 'mouse|touchpad'

	exit 1
fi

DEV="$2"



WIDTH=1920
HEIGHT=1080
APP=weston-terminal

weston --fullscreen --width $WIDTH --height $HEIGHT&
WESTON_PID=$!

sleep 1

export WAYLAND_DISPLAY=wayland-1

$vamos_sources_DIR/src/wldbg/wldbg-source &>wldbg.log &
WLDBG_PID=$!
$vamos_sources_DIR/src/libinput/vsrc-libinput --shmkey /libinput &>libinput.log &
LIBINPUT_PID=$!

sleep 1
./monitor Clients:generic:/vamos-wldbg Libinput:generic:/libinput &> monitor.log &
MONITOR_PID=$!

sleep 1
$APP&
T1_PID=$!
$APP&
T2_PID=$!

xdotool mousemove --sync $((WIDTH/2)) $((HEIGHT/2))
evemu-play $DEV < $1

kill -TERM $T1_PID
kill -TERM $T2_PID
sleep 1

kill -INT $WESTON_PID

wait $MONITOR_PID

#sleep 1
#kill -TERM $LIBINPUT_PID || true
#kill -TERM $WLDBG_PID || true
