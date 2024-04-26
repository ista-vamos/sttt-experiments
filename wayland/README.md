# Wayland experiments

This experiments assume you are running a Linux system with the X window graphical sub-system.
Wayland-based graphical sub-systems are not supported by the scripts,
but our components should work with these too (automatization TBD).

## Building the docker image

```
docker build . -f Dockerfile-wayland  -t  vamos:wayland
```

## Running the docker image

First, identify what device is your touchpad (for instructions with mouse, see later)
by calling either `evemu-describe` or `libinput list-devices`.
You will get a list of devices including information about
the block file called `/dev/input/eventXX` where XX is a number.
This is the file that we need. Once you know the device, run:

```
DEVICE=/dev/input/event17  # replace with your touchpad device
DEVTYPE=touchpad           # set to "mouse" if your device is a mouse and not touchpad

docker run --rm -it  --network host -v /tmp/.X11-unix:/tmp/.X11-unix --env DISPLAY=$DISPLAY  --env XDG_RUNTIME_DIR=/tmp --device /dev/dri/card1 --device $DEVICE --env XAUTH="$(xauth list|grep $(uname -n))" --env DEVTYPE=$DEVTYPE vamos:wayland /bin/bash
```

## Monitor size and multi-monitor setup

Our scripts automatically try to find out the size of the screen.
However, if you use a multi-monitor setup, they can get confused.
In that case,  after starting the docker image, modify the variables
`WIDTH` and `HEIGHT` in the script `run.sh`.

Also, the size of the screen for which we pre-generated events may differ from the size
of the screen you have. If experiments behave weirdly, try recording your own events
as described below and using those.


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

