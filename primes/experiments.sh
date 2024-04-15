#!/bin/bash

set -x
set -e

rm -f /tmp/log.txt

cd $(dirname 0)

source ../setup.sh
export PYTHON_OPTIMIZE=1

#for SHM_BUFSIZE in 1 8 32 64; do
for SHM_BUFSIZE in 8; do
        for ARBITER_BUFSIZE in 128 512 1024 2048; do
		if [ "$PRIMES_10000" = "yes" ] ; then
			for i in `seq 1 $REPEAT`; do
				./run-c.py $SHM_BUFSIZE $ARBITER_BUFSIZE 10000
			done
		else
        for PRIMES_NUM in 10000 20000 30000 40000; do
			    for i in `seq 1 $REPEAT`; do
			    	./run-c.py $SHM_BUFSIZE $ARBITER_BUFSIZE $PRIMES_NUM
			    done
        done
		fi
        done
done
