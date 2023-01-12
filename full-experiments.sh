#!/usr/bin/env bash
cp shamon/experiments/setup.sh .
cp shamon/experiments/setup-full.sh shamon/experiments/setup.sh
cd shamon/experiments/scalability
make experiments
#Experiments commented out due to bug, uncomment to try to run
#cd ../primes
#make experiments
#make experiments-tessla
#cd ../bank
#make experiments
#cd ../bank-tessla
#make experiments
cd ../dataraces
make experiments
cd ../../..
rm shamon/experiments/setup.sh
mv setup.sh shamon/experiments/setup.sh
cd plots
make plots

