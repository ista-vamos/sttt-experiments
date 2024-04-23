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


FROM base-git AS vamos

COPY --from=dynamorio /opt/dynamorio/build /opt/dynamorio/build
WORKDIR /opt
# Install LLVM and clang
RUN apt-get install -y --no-install-recommends clang llvm-dev

# Clone VAMOS and copy the experiments
RUN git clone --depth=1 https://github.com/ista-vamos/vamos -b sttt
COPY . /opt/vamos/sttt-experiments
WORKDIR /opt/vamos/sttt-experiments
RUN git clean -xdf
#compile VAMOS
WORKDIR /opt/vamos
RUN make -j2 CC=clang CXX=clang++ BUILD_TYPE=Debug DynamoRIO_DIR=/opt/dynamorio/build/cmake\
	LIBINPUT_SOURCES=OFF WLDBG_SOURCES=OFF
# copy and setup the experiments
RUN make sttt-experiments DynamoRIO_DIR=/opt/dynamorio/build/cmake

FROM base as prepare-artifact
RUN mkdir /opt/results
RUN apt-get install -y --no-install-recommends\
        cargo\
	clang \
        valgrind\
	python3-matplotlib\
	python3-pandas\
	python3-seaborn\
	llvm\
	libclang-rt-dev

FROM prepare-artifact as artifact
COPY --from=vamos /opt/vamos /opt/vamos
COPY --from=dynamorio /opt/dynamorio/build /opt/dynamorio/build
WORKDIR /opt/vamos/sttt-experiments

