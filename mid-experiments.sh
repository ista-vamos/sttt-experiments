#!/usr/bin/env bash
set -e
cd $(dirname $0)

cp setup.sh setup-old.sh
cp scripts/setup-mid.sh setup.sh

scripts/run-experiments.sh

cd $(dirname $0)
mv setup-old.sh setup.sh

make -C plots clean
make -C plots plots
make -C plots original
