include ../Makefile.config

CPPFLAGS=
CFLAGS=-O3

all: prepare

COMPILER_CFILES=${vamos_compiler_DIR}/compiler/cfiles/

compiler_utils.o: ${COMPILER_CFILES}/compiler_utils.c
	$(CC) -I${vamos_buffers_INCLUDE_DIRS} -c $< -o compiler_utils.o

intmap.o: ${COMPILER_CFILES}/intmap.cpp
	$(CXX) -c $< -o intmap.o

prepare: primes primes-bad  compiler_utils.o intmap.o
	python3 shm_prepare_programs.py

prepare-tessla: primes primes-bad  compiler_utils.o intmap.o

primes: primes.c

manualprimes: manualprimes.c
	$(CC) -I${vamos_buffers_INCLUDE_DIRS} manualprimes.c -o manualprimes -L${vamos_buffers_LIBRARIES_DIRS} ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-source.a ${vamos_buffers_LIBRARIES_DIRS_shmbuf}/libvamos-buffers-shmbuf.a ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-ringbuf.a ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-utils.a ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-signature.a ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-event.a ${vamos_buffers_LIBRARIES_DIRS_core}/libvamos-buffers-list.a

primes-bad: primes-bad.c

experiments: prepare
	./experiments.sh

experiments-tessla:
	./experiments-tessla.sh

clean:
	-rm *.o primes primes-bad
	-rm -rf __pycache__

.PHONY: clean all experiments experiments-tessla
