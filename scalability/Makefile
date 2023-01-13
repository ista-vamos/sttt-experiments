include ../Makefile.config

all: source monitor

CC=clang
CFLAGS=-g3 -O3 -flto -fno-fat-lto-objects -fPIC -std=c11
CPPFLAGS=-D_POSIX_C_SOURCE=200809L -DNDEBUG
LDFLAGS=-lpthread

MON_COMPILER_PY=${vamos_compiler_DIR}/compiler/main.py
MON_COMPILER=${vamos_compiler_DIR}/gen/compile.sh

SOURCE_LIBS=$(shamon_LIBRARIES_DIRS_shmbuf)/libshamon-shmbuf.a\
            $(shamon_LIBRARIES_DIRS_core)/libshamon-source.a\
            $(shamon_LIBRARIES_DIRS_core)/libshamon-signature.a\
            $(shamon_LIBRARIES_DIRS_core)/libshamon-ringbuf.a\
            $(shamon_LIBRARIES_DIRS_core)/libshamon-event.a\
            $(shamon_LIBRARIES_DIRS_core)/libshamon-list.a\
            $(shamon_LIBRARIES_DIRS_core)/libshamon-utils.a

MONITOR_LIBS= ${shamon_LIBRARIES_DIRS_core}/libshamon-signature.a\
              ${shamon_LIBRARIES_DIRS_core}/libshamon.a\
              ${shamon_LIBRARIES_DIRS_core}/libshamon-arbiter.a\
              ${shamon_LIBRARIES_DIRS_core}/libshamon-parallel-queue.a\
              ${shamon_LIBRARIES_DIRS_core}/libshamon-ringbuf.a\
              ${shamon_LIBRARIES_DIRS_core}/libshamon-event.a\
              ${shamon_LIBRARIES_DIRS_streams}/libshamon-streams.a\
	      ${shamon_LIBRARIES_DIRS_shmbuf}/libshamon-shmbuf.a\
              ${shamon_LIBRARIES_DIRS_core}/libshamon-utils.a

source.o: source.c
	$(CC) -c $(CFLAGS) source.c -I ${shamon_INCLUDE_DIRS}

source: source.o
	$(CC) $(CFLAGS) source.o -o source $(SOURCE_LIBS)

monitor.c: monitor.txt
	python3 $(MON_COMPILER_PY) -freq 10000000 monitor.txt -o monitor.c
	-clang-format -i monitor.c

monitor: monitor.c
	$(MON_COMPILER) monitor.c

experiments:
	python3 -O -m compileall *.py
	./experiments.sh

.PHONY clean:
	-rm monitor.c monitor.txt
	-rm *.o monitor source
	-rm -rf __pycache__

