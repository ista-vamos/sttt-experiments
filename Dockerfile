FROM ubuntu:20.04 AS base

RUN set -e

ENV DEBIAN_FRONTEND=noninteractive

# Install packages
RUN apt-get -y update
RUN apt-get install -y --no-install-recommends\
        python3\
        python3-pip\
        g++\
        gcc\
        make\
        time

FROM base AS llvm
RUN apt-get install -y --no-install-recommends\
        gnupg\
        lsb-release\
        software-properties-common\
        wget

# Install LLVM 14
RUN wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh &&\
    sed -i 's@PKG="clang-$LLVM_VERSION.*@PKG="clang-$LLVM_VERSION"@' ./llvm.sh &&\
    ./llvm.sh 14 &&\
    ln -s /usr/bin/clang-14 /usr/bin/clang &&\
    ln -s /usr/bin/clang++-14 /usr/bin/clang++ &&\
    ln -s /usr/bin/llvm-link-14 /usr/bin/llvm-link &&\
    ln -s /usr/bin/llvm-config-14 /usr/bin/llvm-config &&\
    ln -s /usr/bin/opt-14 /usr/bin/opt

FROM llvm as vamos
RUN apt-get install -y --no-install-recommends\
        cmake\
        git

# clone VAMOS
WORKDIR /opt
RUN git clone https://github.com/ista-vamos/vamos -b main
WORKDIR /opt/vamos

# compile DynamoRIO and then VAMOS
RUN make sources-init && make -j4 -C vamos-sources/ext dynamorio BUILD_TYPE=RelWithDebInfo
RUN make -j4

FROM vamos AS experiments
# copy the experiments
COPY . /opt/vamos/fase23-experiments

# compile the experiments
RUN make fase23-experiments
WORKDIR /opt/vamos/fase23-experiments

FROM llvm as prepare-artifact
RUN pip install matplotlib==3.6.0 pandas==1.5.0 seaborn==0.12.0 && mkdir /opt/results
RUN apt-get install -y --no-install-recommends\
	cargo\
        openjdk-17-jdk\
        valgrind

FROM prepare-artifact as artifact
COPY --from=experiments /opt/vamos /opt/vamos
#COPY --from=llvm /usr/bin/clang\
#                 /usr/bin/clang++\
#                 /usr/bin/llvm-link\
#                 /usr/bin/opt\
#                 /usr/bin/
#COPY --from=llvm /lib/x86_64-linux-gnu/libclang-cpp.so.14\
#                 /lib/x86_64-linux-gnu/libLLVM-14.so.1\
#                 /lib/x86_64-linux-gnu/
#COPY --from=llvm /usr/lib/gcc/ /usr/lib/gcc
#COPY --from=llvm /usr/lib/llvm-14/ /usr/lib/llvm-14/


# "install" TSan for dataraces experiments
# for some reason we cannot install TSan normally
# Install packages for generating plots and prepare the dir for results
COPY ./dataraces/libclang_rt.tsan-x86_64.a /usr/lib/llvm-14/lib/clang/14.0.6/lib/linux/libclang_rt.tsan-x86_64.a

WORKDIR /opt/vamos/fase23-experiments
