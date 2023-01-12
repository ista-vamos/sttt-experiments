#!/usr/bin/env bash
set -e
cd $(dirname $0)

cp setup.sh setup-old.sh
cp scripts/setup-full.sh setup.sh

scripts/run-experiments.sh

cd $(dirname $0)
mv setup-old.sh setup.sh

#cd plots
#make plots

