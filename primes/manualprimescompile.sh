#!/usr/bin/env bash

set +x

SELFDIR="/opt/vamos/vamos-compiler"
SHAMON_INCLUDE_DIR="/opt/vamos/vamos-buffers/cmake/vamos-buffers/../../include"
CC=clang
CPPFLAGS="-D_POSIX_C_SOURCE=200809L -I$SELFDIR -I$SHAMON_INCLUDE_DIR\
          -I$SHAMON_INCLUDE_DIR/streams -I$SHAMON_INCLUDE_DIR/core -I$SHAMON_INCLUDE_DIR/shmbuf"

LTOFLAGS=""
CFLAGS="-g -O0"

LIBRARIES="/opt/vamos/vamos-buffers/src/core/libvamos-buffers-arbiter.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-stream.a\
          /opt/vamos/vamos-buffers/src/shmbuf/libvamos-buffers-shmbuf.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-parallel-queue.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-ringbuf.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-event.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-source.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-signature.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-list.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-utils.a\
          /opt/vamos/vamos-buffers/src/core/libvamos-buffers-monitor-buffer.a\
          /opt/vamos/vamos-buffers/src/streams/libvamos-buffers-streams.a\
          $SELFDIR/compiler/cfiles/compiler_utils.o\
          /opt/vamos/vamos-compiler/compiler/cfiles/intmap.o\
          -lstdc++"

EXECUTABLEPATH="/opt/fase23-experiments/primes/monitor"
CFILEPATH="/tmp/vamos_monitor.c"

test -z $CC && CC=cc
${CC} -I$SHAMON_INCLUDE_DIR -c $CFLAGS $SELFDIR/compiler/cfiles/compiler_utils.c -o $SELFDIR/compiler/cfiles/compiler_utils.o
${CC} $CFLAGS $LTOFLAGS $CPPFLAGS -o $EXECUTABLEPATH $CFILEPATH $@ $LIBRARIES $LDFLAGS
