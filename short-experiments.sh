#!/usr/bin/env bash
set -e
cd $(dirname $0)

cp setup.sh setup-old.sh
cp scripts/setup-short.sh setup.sh

scripts/run-experiments.sh

rm shamon/experiments/setup.sh
mv setup-old.sh setup.sh

#cd plots
#make plots

