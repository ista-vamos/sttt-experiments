#!/usr/bin/env bash
cp shamon/experiments/setup.sh .
cp shamon/experiments/setup-short.sh shamon/experiments/setup.sh
cd shamon/experiments/scalability
make experiments
cd ../dataraces
make experiments
cd ../../..
rm shamon/experiments/setup.sh
mv setup.sh shamon/experiments/setup.sh
cd plots
make plots

