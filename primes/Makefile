include ../Makefile.config

CPPFLAGS=
CFLAGS=-O3

all: prepare

COMPILER_CFILES=${vamos_compiler_DIR}/compiler/cfiles/

compiler_utils.o: ${COMPILER_CFILES}/compiler_utils.c
	$(CC) -I${shamon_INCLUDE_DIRS} -c $< -o compiler_utils.o

intmap.o: ${COMPILER_CFILES}/intmap.cpp
	$(CXX) -c $< -o intmap.o

prepare: primes primes-bad  compiler_utils.o intmap.o
	python3 shm_prepare_programs.py

primes: primes.c

primes-bad: primes-bad.c

experiments: prepare
	./experiments.sh

experiments-tessla:
	./experiments-tessla.sh

clean:
	-rm *.o primes primes-2 primes-bad
	-rm -rf __pycache__

.PHONY: clean all experiments experiments-tessla
