#!/bin/bash

set -e

cd $(dirname 0)

rm -f log.txt


source ../setup.sh
source ../setup-vars.sh

test -z $BANK_NUM && BANK_NUM=100000
SHM_BUFSIZE=1
# RUNDIR="$(dirname $0)/rundata$(date +%Y%m%d-%H%M%S)"
# mkdir $RUNDIR
RUNDIR="$(dirname $0)"
export PYTHON_OPTIMIZE=1

echo "Logs of make are in /tmp/make*.txt"

for ARBITER_BUFSIZE in 4 16 32 64 128 256 512 1024 2048; do
	echo "** SHM BUFSIZE: $SHM_BUFSIZE page, ARBITER_BUFSIZE: $ARBITER_BUFSIZE **"
	echo " - Generating the monitor"
	make -j4 BUFSIZE=$ARBITER_BUFSIZE 1>> $RUNDIR/make.stdout.txt 2>> $RUNDIR/make.stderr.txt

	for i in `seq 1 $REPEAT`; do
	echo " - Running"
	./regexbank.sh $BANK_NUM $ARBITER_BUFSIZE >$RUNDIR/out-$SHM_BUFSIZE-$ARBITER_BUFSIZE-$BANK_NUM-$i.txt 2>$RUNDIR/err-$SHM_BUFSIZE-$ARBITER_BUFSIZE-$BANK_NUM-$i.txt
	python3 parse_results.py $RUNDIR/out-$SHM_BUFSIZE-$ARBITER_BUFSIZE-$BANK_NUM-$i.txt 0 >> $RUNDIR/bank-$SHM_BUFSIZE-$ARBITER_BUFSIZE-$BANK_NUM.csv
	done

	for ERR_FREQ in 5 10 100 1000; do
	    echo " - Running with $ERR_FREQ errors freq"
	    ./regexbank.sh $BANK_NUM $ARBITER_BUFSIZE errors $ERR_FREQ >$RUNDIR/out-$SHM_BUFSIZE-$ARBITER_BUFSIZE-$BANK_NUM-ERR-$ERR_FREQ-$i.txt 2>$RUNDIR/err-$SHM_BUFSIZE-$ARBITER_BUFSIZE-$BANK_NUM-ERR-$ERR_FREQ-$i.txt
	    python3 parse_results.py $RUNDIR/out-$SHM_BUFSIZE-$ARBITER_BUFSIZE-$BANK_NUM-ERR-$ERR_FREQ-$i.txt $ERR_FREQ >> $RUNDIR/bank-$SHM_BUFSIZE-$ARBITER_BUFSIZE-$BANK_NUM-ERR-$ERR_FREQ.csv
    done
done

