include ../Makefile.config

all: source monitor

CC=clang
CFLAGS=-g3 -O3 -flto -fno-fat-lto-objects -fPIC -std=c11
CPPFLAGS=-D_POSIX_C_SOURCE=200809L -DNDEBUG
LDFLAGS=-lpthread

MON_COMPILER_PY=${vamos_compiler_DIR}/compiler/vamosc.py
#MON_COMPILER=${vamos_compiler_DIR}/gen/compile.sh

SOURCE_LIBS=$(vamos_buffers_LIBRARIES_DIRS_shmbuf)/libvamos-buffers-shmbuf.a\
            $(vamos_buffers_LIBRARIES_DIRS_core)/libvamos-buffers-source.a\
            $(vamos_buffers_LIBRARIES_DIRS_core)/libvamos-buffers-signature.a\
            $(vamos_buffers_LIBRARIES_DIRS_core)/libvamos-buffers-ringbuf.a\
            $(vamos_buffers_LIBRARIES_DIRS_core)/libvamos-buffers-event.a\
            $(vamos_buffers_LIBRARIES_DIRS_core)/libvamos-buffers-list.a\
            $(vamos_buffers_LIBRARIES_DIRS_core)/libvamos-buffers-utils.a

MONITOR_LIBS= ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-signature.a\
              ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers.a\
              ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-arbiter.a\
              ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-parallel-queue.a\
              ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-ringbuf.a\
              ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-event.a\
              ${vamos_buffers_LIBRARIES_DIRS_streams}/libvamos-buffers-streams.a\
	      ${vamos_buffers_LIBRARIES_DIRS_shmbuf}/libvamos-buffers-shmbuf.a\
              ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-utils.a

source.o: source.c
	$(CC) -c $(CFLAGS) source.c -I ${vamos_buffers_INCLUDE_DIRS}

source: source.o
	$(CC) $(CFLAGS) source.o -o source $(SOURCE_LIBS)

monitor: monitor.txt
	python3 $(MON_COMPILER_PY) --nondeterministic-conditions -freq 10000000 monitor.txt -e monitor

#monitor: monitor.c
	#-clang-format -i monitor.c
	#$(MON_COMPILER) monitor.c

experiments:
	python3 -O -m compileall *.py
	./experiments.sh

.PHONY clean:
	-rm monitor.c monitor.txt
	-rm *.o monitor source
	-rm -rf __pycache__

