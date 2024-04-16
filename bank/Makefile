include ../Makefile.config

CPPFLAGS=
CFLAGS=-g #-O3
VLCC=python3 ${vamos_compiler_DIR}/compiler/vamosc.py
GENCC=${vamos_compiler_DIR}/gen/compile.sh
SHAMON_LIB=${vamos_buffers_libraries_DIR}/libvamos-buffers-lib.so  # for dependency

all: monitor-vamos bank interact

intmap.o: ${vamos_compiler_DIR}/compiler/cfiles/intmap.cpp
	$(CXX) -c $<

$(VLCC):  # empty, just a depenency for monitor
$(GENCC):
$(SHAMON_LIB):

interact: interact.c
	$(CC) $^ $(CFLAGS) $(CPPFLAGS) -o $@ -g

monitor-vamos: bankmonitor.vl  $(VLCC) $(SHAMON_LIB) intmap.o
	$(VLCC) bankmonitor.vl --nondeterministic-conditions -e monitor-vamos -Lstdc++ -l intmap.o

bank.o : bank.c bank.h
	$(CC) -c $< $(CFLAGS) $(CPPFLAGS) -o $@

client.o : client.c bank.h common.h
	$(CC) -c $< $(CFLAGS) $(CPPFLAGS) -o $@

bank: client.o bank.o
	$(CC) $^ $(CFLAGS) $(CPPFLAGS) -o $@ -lpthread

experiments: interact
	./experiments.sh

clean:
	-rm *.o monitor-vamos monitor-tessla bank interact *.o

.PHONY: clean all experiments
