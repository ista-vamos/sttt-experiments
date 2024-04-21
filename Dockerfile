FROM ubuntu:23.04 AS base

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

FROM base AS base-git
RUN apt-get install -y --no-install-recommends\
        cmake\
        git

FROM base-git AS dynamorio
WORKDIR /opt
#RUN apt-get install -y --no-install-recommends patch
RUN git clone --depth=1 https://github.com/DynamoRIO/dynamorio -b release_10.0.0 &&\
    mkdir -p dynamorio/build &&\
    cd dynamorio/build &&\
    cmake .. &&\
    make -j4


# clone VAMOS
FROM base-git AS vamos
WORKDIR /opt
# Install LLVM and clang
RUN apt-get install -y --no-install-recommends clang llvm-dev
# Install pkg-config for libinput sources
#RUN apt-get install -y --no-install-recommends pkg-config #libevdev-dev libinput-dev autoconf automake autotools-dev libtool
#RUN apt-get install -y --no-install-recommends libwayland-dev weston

WORKDIR /opt
RUN git clone --depth=1 https://github.com/ista-vamos/vamos -b sttt
#compile VAMOS
WORKDIR /opt/vamos
COPY --from=dynamorio /opt/dynamorio/build /opt/dynamorio/build
#RUN git submodule update --init --recursive
#RUN cd vamos-sources && make -C ext wldbg
RUN make -j2 CC=clang CXX=clang++ BUILD_TYPE=Debug DynamoRIO_DIR=/opt/dynamorio/build/cmake\
	LIBINPUT_SOURCES=OFF WLDBG_SOURCES=OFF
# copy and setup the experiments
# COPY . /opt/vamos/sttt-experiments
RUN make sttt-experiments DynamoRIO_DIR=/opt/dynamorio/build/cmake 

FROM base as prepare-artifact
RUN mkdir /opt/results
# again install LLVM -- if we try to copy it, it gets broken
RUN apt-get install -y --no-install-recommends\
        cargo\
	clang \
        #openjdk-17-jdk\
        valgrind\
	python3-matplotlib\
	python3-pandas\
	python3-seaborn

FROM prepare-artifact as artifact
COPY --from=vamos /opt/vamos /opt/vamos
COPY --from=dynamorio /opt/dynamorio/build /opt/dynamorio/build
WORKDIR /opt/vamos/sttt-experiments

# "install" TSan for dataraces experiments
# for some reason we cannot install TSan normally
# Install packages for generating plots and prepare the dir for results
# COPY ./dataraces/libclang_rt.tsan-x86_64.a /usr/lib/llvm-14/lib/clang/14.0.6/lib/linux/libclang_rt.tsan-x86_64.a

