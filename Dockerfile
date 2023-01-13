FROM ubuntu:20.04

RUN set -e

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update  &&\
    apt-get install -y python3 make cmake gcc g++ git lsb-release wget software-properties-common gnupg

WORKDIR /tmp
RUN wget https://apt.llvm.org/llvm.sh
RUN chmod +x llvm.sh
RUN ./llvm.sh 14

RUN ln -s /usr/bin/clang-14 /usr/bin/clang
RUN ln -s /usr/bin/clang++-14 /usr/bin/clang++
RUN ln -s /usr/bin/llvm-link-14 /usr/bin/llvm-link
RUN ln -s /usr/bin/llvm-config-14 /usr/bin/llvm-config
RUN ln -s /usr/bin/opt-14 /usr/bin/opt

# Other packages needed by the experiments
RUN apt-get install -y time valgrind openjdk-17-jdk cargo python3-pip

# clone VAMOS
WORKDIR /opt
RUN git clone https://github.com/ista-vamos/vamos
WORKDIR /opt/vamos

# compile DynamoRIO and then VAMOS
RUN make sources-init
RUN make -j4 -C vamos-sources/ext dynamorio BUILD_TYPE=RelWithDebInfo
RUN make -j4

# copy the experiments
COPY . /opt/vamos/fase23-experiments
RUN make fase23-experiments
WORKDIR /opt/vamos/fase23-experiments

# Packages for generating plots
RUN pip install -r plots/scripts/requirements.txt
# Directory for results
RUN mkdir /opt/results

# for some reason we cannot install TSan normally
RUN mkdir -p /usr/lib/llvm-14/lib/clang/14.0.6/lib/linux/
RUN cp dataraces/libclang_rt.tsan-x86_64.a /usr/lib/llvm-14/lib/clang/14.0.6/lib/linux/libclang_rt.tsan-x86_64.a

