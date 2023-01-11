#!/bin/bash

set -e

cd $(dirname 0)

rm -f log.txt

source ../setup.sh

echo "Logs of make are in /tmp/make*.txt"

for i in `seq 1 $REPEAT`; do
	echo "-- run.sh --"
        ./run.sh
done
