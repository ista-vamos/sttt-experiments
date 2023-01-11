#!/bin/bash

set -e

DIR=$(dirname $0)
source $DIR/../setup-vars.sh

SOURCESDIR="$vamos_sources_DIR"
NUM=$1
test -z $NUM && NUM=10000

CMAKE_CACHE="$SOURCESDIR/CMakeCache.txt"
LINE=$(grep "DynamoRIO_DIR" "$CMAKE_CACHE")
DRIOROOT="${LINE#*=}/.."
if [ ! -d $DRIOROOT ]; then
       DRIOROOT="$SOURCESDIR/ext/dynamorio/build"
fi
if [ ! -d $DRIOROOT ]; then
	DRIOROOT=/opt/dynamorio/build
fi

DRRUN="$DRIOROOT/bin64/drrun"
if [ ! -x $DRRUN ]; then
	echo "Could not find drrun"
	exit 1
fi

$DRRUN -root $DRIOROOT \
	-opt_cleancall 2 -opt_speed\
	-c $SOURCESDIR/drregex/libdrregex.so\
	/primes1 prime '#([0-9]+): ([0-9]+)' ii --\
	$DIR/primes $NUM &

$DRRUN -root $DRIOROOT \
	-opt_cleancall 2 -opt_speed\
	-c $SOURCESDIR/drregex/libdrregex.so\
	/primes2 prime '#([0-9]+): ([0-9]+)' ii --\
	$DIR/primes-bad $NUM 10&

wait
wait
