#!/bin/bash

set -e

REP=3

cd $(dirname $0)
rm -f results-*.csv

source ../setup.sh

export DATARACES_REPEAT_RUN

# some benchmark contain assertions that can be violated,
# do not dump core file in such cases
ulimit -c 0

for I in `seq 1 $DATARACES_HARNESS_NUM`; do
	if [ "$DATARACES_SHORT" = "yes" ]; then
		for FILE in $(ls benchmarks/fib*.i); do
			python3 ./run.py $FILE results.csv;
		done
		for FILE in $(ls benchmarks/big*.i); do
			python3 ./run.py $FILE results.csv;
		done
		for FILE in $(ls benchmarks/pthread*.i); do
			python3 ./run.py $FILE results.csv;
		done
	else
		for FILE in $(ls benchmarks/*.i); do
			python3 ./run.py $FILE results.csv;
		done
	fi
done
