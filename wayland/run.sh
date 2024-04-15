#!/bin/bash
#

set -e
set -x

cd $(dirname $0)
weston&
export WAYLAND_DISPLAY=wayland-1
sleep 1
src/wldbg/wldbg-source&
src/libinput/vsrc-libinput --shmkey /tmp&
