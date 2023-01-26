#!/bin/bash

set -e

DIR=$(dirname $0)
cd $DIR

source ../setup.sh

# every generated binary will be run `DATARACES_REPEAT_RUN` times,
# so in total, each benchmark will be executed for each tool
# `DATARACES_REPEAT_RUN*REPEAT` times.

export DATARACES_REPEAT_RUN

# Always use the same harness for reproducibility.
# Comment this out if you want to use random harnesses
# for each execution of `run.py`.
export DATARACES_HARNESS="$DIR/harness.c"

# some benchmark contain assertions that can be violated,
# do not dump core file in such cases
ulimit -c 0

for I in `seq 1 $REPEAT`; do
	if [ "$DATARACES_NONDETS" = "yes" ]; then
		for FILE in $(ls benchmarks/*.i); do
			python3 ./run.py $FILE results.csv;
		done
	else
		for FILE in $(cat benchmarks/deterministic.txt); do
			python3 ./run.py "benchmarks/$FILE" results.csv;
		done
	fi
done
