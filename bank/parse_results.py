#!/usr/bin/python3

from sys import argv

infile = argv[1]
ERR_FREQ=argv[2]

errors_generated = 0
with open(infile, 'r') as f:
    for line in f:
        if "in_holes" in line:
            parts = line.split()
            in_holes, out_holes = int(parts[1][:-1]), int(parts[3])
        if "in_dropped" in line:
            parts = line.split()
            in_drop, out_drop = int(parts[1][:-1]), int(parts[3])
        elif "Errors found" in line:
            parts = line.split()
            errors = int(parts[2])
        elif "Errors generated" in line:
            parts = line.split()
            errors_generated = int(parts[2])
        elif "Time:" in line:
            parts = line.split()
            time = float(parts[1])

print(",".join(map(str, [ERR_FREQ, errors_generated, errors, time, in_holes, out_holes, in_drop, out_drop])))
