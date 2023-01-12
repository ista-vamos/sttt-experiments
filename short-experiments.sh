#!/usr/bin/env bash
set -e
cd $(dirname $0)

cp setup.sh setup-old.sh
cp scripts/setup-short.sh setup.sh

scripts/run-experiments.sh

cd $(dirname $0)
mv setup-old.sh setup.sh

make plots -C plots
make plots -C original

