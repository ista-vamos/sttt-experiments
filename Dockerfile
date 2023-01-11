FROM ubuntu:20.04

RUN set -e

ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt -y update  &&\
    apt install -y python3 make cmake gcc g++ git lsb-release wget software-properties-common gnupg

WORKDIR /tmp
RUN wget https://apt.llvm.org/llvm.sh
RUN chmod +x llvm.sh
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    ./llvm.sh 14 all

RUN ln -s /usr/bin/clang-14 /usr/bin/clang
RUN ln -s /usr/bin/clang++-14 /usr/bin/clang++
RUN ln -s /usr/bin/llvm-link-14 /usr/bin/llvm-link
RUN ln -s /usr/bin/llvm-config-14 /usr/bin/llvm-config
RUN ln -s /usr/bin/opt-14 /usr/bin/opt

WORKDIR /opt

RUN git clone https://github.com/ista-vamos/vamos
WORKDIR /opt/vamos

RUN make sources-init
RUN make -j4 -C vamos-sources/ext dynamorio BUILD_TYPE=RelWithDebInfo
RUN make -j4

# Other packages needed by the experiments

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt install -y time valgrind openjdk-17-jdk cargo

# for some reason we cannot install this normally
RUN apt-get download -y libclang-rt-14-dev
RUN ar x libclang-rt-14*.deb
RUN tar xf data.tar.xz ./usr/lib/llvm-14/lib/clang/14.0.6/lib/linux/libclang_rt.tsan-x86_64.a
RUN mv ./usr/lib/llvm-14/lib/clang/14.0.6/lib/linux/libclang_rt.tsan-x86_64.a /usr/lib/llvm-14/lib/clang/14.0.6/lib/linux/libclang_rt.tsan-x86_64.a

# copy the experiments
COPY . /opt/vamos/experiments
RUN make experiments
WORKDIR /opt/vamos/experiments

# CMD ["/bin/bash"]
