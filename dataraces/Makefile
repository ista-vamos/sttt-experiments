include ../Makefile.config

ARBITER_BUFFER:=2048

CXX=clang++
CXXFLAGS=
CFLAGS=-fPIC -std=c11
CPPFLAGS=-D_POSIX_C_SOURCE=200809L
LDFLAGS=-lpthread

ifdef DEBUG
CFLAGS += -g -O0
CXXFLAGS += -g -O0
CPPFLAGS += -DDBGBUF
else # DEBUG
ifeq ($(vamos_buffers_BUILD_TYPE), Debug)
CFLAGS +=-g -O0
CXXFLAGS +=-g -O0
else
CFLAGS +=-g3 -O3 -flto -fno-fat-lto-objects
CXXFLAGS +=-g3 -O3 -flto -fno-fat-lto-objects
CPPFLAGS += -DNDEBUG
endif
endif

MON_COMPILER_PY=$(vamos_compiler_DIR)/compiler/vamosc.py
MON_COMPILER=$(vamos_compiler_DIR)/gen/compile.sh

all: monitor

monitor.o: monitor.cpp
	$(CXX) -I$(vamos_buffers_INCLUDE_DIRS) $(CXXFLAGS) $(CPPFLAGS) $(MONITOR_CPP_FLAGS) monitor.cpp -std=c++17 -c

monitor: monitor.txt monitor.o compiler_utils.o clean
	python3 $(MON_COMPILER_PY) monitor.txt -b $(ARBITER_BUFFER) -e monitor -Lstdc++ -l compiler_utils.o -l monitor.o

compiler_utils.o: $(vamos_compiler_DIR)/compiler/cfiles/compiler_utils.c
	$(CC) -g -c $<  -I$(vamos_buffers_INCLUDE_DIRS) -o $@

run: monitor
	./monitor Program:generic:/vrd

experiments: monitor
	./experiments.sh

clean:
	-rm monitor.c *.bc *.o vgcore*

.PHONY: all clean


