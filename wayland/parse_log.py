import sys

# Wayland motion events: 1070
# Libinput motion events: 1116
# Wayland motions compared: 1019
# Segments: 54
# Wayland motions matched: 813
# Wayland motions NOT matched: 206
# Holes: 0
wme, lme, wmc, seg, match, err, holes = 0, 0, 0, 0, 0, 0, 0

with open(sys.argv[1], "r") as f:
    for line in f:
        if line.startswith("Wayland motion events"):
            wme = int(line.split()[3])
        elif line.startswith("Libinput motion events"):
            lme = int(line.split()[3])
        elif line.startswith("Wayland motions compared"):
            wmc = int(line.split()[3])
        elif line.startswith("Segments"):
            seg = int(line.split()[1])
        elif line.startswith("Wayland motions matched"):
            match = int(line.split()[3])
        elif line.startswith("Wayland motions NOT matched"):
            err = int(line.split()[4])
        elif line.startswith("Holes"):
            holes = int(line.split()[1])

print(",".join(map(str, (wme, lme, wmc, seg, match, err, holes))))
