## Running the docker image

First, identify what device is your touchpad (for instructions with mouse, see later)
by calling either `evemu-describe` or `libinput list-devices`.
You will get a list of devices including information about
the block file called `/dev/input/eventXX` where XX is a number.
This is the file that we need. Once you know the device, run:

```
DEVICE=/dev/input/event17  # replace with your touchpad device
DEV_IS_MOUSE=0             # set to 1 if your device is a mouse and not touchpad

docker run --rm -it  --network host -v /tmp/.X11-unix:/tmp/.X11-unix --env DISPLAY=$DISPLAY  --env XDG_RUNTIME_DIR=/tmp --device /dev/dri/card1 --device $DEVICE --env XAUTH="$(xauth list|grep $(uname -n))" --env DEV_IS_MOUSE=$DEV_IS_MOUSE vamos:wayland /bin/bash
```

## Using your own events

To use your own events, you must record them first. Run:
```
evemu-record > events.txt
```

The command will ask you about the device to use. Select your mouse/touchpad and then
move it around. When you are done, press Ctrl-C. If you want to make sure that you
have selected the right device, you may run the command without `> events.txt`
and you will see the events generated on the fly while moving the mouse/touchpad.

If you want to use your generated events in the experiments, simply
rewrite the pre-defined files with events (e.g., `mouse-events1.txt`) with your events.


### Troubleshooting X11 permisisons

In the case that X11 denies running weston, try run this on host system: 
```
xhost +
```

Warning: this will disable all X11 permisisons checking on your system,
so you may want run `xhost -` (or reboot).