#!/bin/bash
echo "***** Installing Prerequisites *****"

cd packages
sudo dpkg -i *.deb
cd ..

cd pip
pip3 install *.whl
cd ..

cat rustsplit* > rust-1.66.0-x86_64-unknown-linux-gnu.tar.gz
tar -xzf rust-1.66.0-x86_64-unknown-linux-gnu.tar.gz
cd rust-1.66.0-x86_64-unknown-linux-gnu
sudo ./install.sh
cd ..

echo "***** Setting up local folders *****"

sudo mkdir /opt/vamos
sudo chown fase2023:fase2023 /opt/vamos

sudo mv dynamorio /opt/vamos/dynamorio
sudo mv shamon /opt/vamos/shamon
sudo mv plots /opt/vamos/plots
sudo mv initial-tests.sh /opt/vamos/initial-tests.sh
sudo mv run-repetition.sh /opt/vamos/run-repetition.sh
sudo mv tessla-assembly-1.2.3 /opt/vamos/shamon/experiments/tessla/tessla-rust.jar

cd /opt/vamos
sudo chown -R fase2023:fase2023 *.sh
sudo chown -R fase2023:fase2023 dynamorio
sudo chown -R fase2023:fase2023 shamon
sudo chown -R fase2023:fase2023 plots

echo "***** Building DynamoRIO *****"

cd dynamorio
mkdir build
cd build
cmake ..
make -j
cd ../..

echo "***** Building Vamos *****"

cd shamon
cmake -DDynamoRIO_DIR=/opt/vamos/dynamorio/build/cmake/ .
make
cd compiler/cfiles
g++ -c intmap.cpp
gcc -c compiler_utils.c
cd ../..

