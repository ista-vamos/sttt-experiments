include ../Makefile.config

CPPFLAGS=
CFLAGS=-g #-O3
VLCC=python3 ${vamos_compiler_DIR}/compiler/main.py
GENCC=${vamos_compiler_DIR}/gen/compile.sh
SHAMON_LIB=${vamos_buffers_libraries_DIR}/libvamos-buffers-lib.so  # for dependency

BUFSIZE=1024
TESSLA_JAR=$(vamos_compiler_DIR)/compiler/tessla-rust.jar

all: monitor$(BUFSIZE) ../bank/bank ../bank/interact

tesslamon/Cargo.toml: bank.tessla
	test -e $(TESSLA_JAR) || echo "Download TeSSLa Rust bundle from https://www.tessla.io/download/ and rename it to $(TESSLA_JAR)"
	java -jar $(TESSLA_JAR) compile-rust -p tesslamon bank.tessla
	cat vendor.txt >> tesslamon/Cargo.toml
	cp -r vendor tesslamon/vendor

../bank/interact:
	make -C ../bank interact

../bank/bank:
	make -C ../bank bank

bankmonitor-$(BUFSIZE).vl: bankmonitor.vl.in
	sed 's/@BUFSIZE/$(BUFSIZE)/' bankmonitor.vl.in > bankmonitor-$(BUFSIZE).vl

monitor$(BUFSIZE): bankmonitor-$(BUFSIZE).vl tesslamon/Cargo.toml intmap.o
	$(VLCC) -e monitor$(BUFSIZE) -t -d tesslamon bankmonitor-$(BUFSIZE).vl\
		-l intmap.o -Lstdc++ -l tesslamon/target/release/libmonitor.a -Ldl

tesslamon/target/release/libmonitor.a: bankmonitor-$(BUFSIZE).c tesslamon/Cargo.toml
	-cd ./tesslamon; cargo build --release

intmap.o: $(vamos_compiler_DIR)/compiler/cfiles/intmap.*
	g++ -c $< -o $@

#monitor$(BUFSIZE): tesslamon/target/release/libmonitor.a bankmonitor-$(BUFSIZE).c intmap.o
#	#NOLTO=yes $(GENCC) bankmonitor-$(BUFSIZE).c intmap.o -lstdc++ tesslamon/target/release/libmonitor.a -ldl
#	$(GENCC) bankmonitor-$(BUFSIZE).c intmap.o -lstdc++ tesslamon/target/release/libmonitor.a -ldl
#	mv monitor monitor$(BUFSIZE)

experiments: ../bank/interact ../bank/bank
	./experiments.sh

clean:
	-rm bankmonitor-*.c bankmonitor-*.vl *.o monitor* *.o
	-rm out*.txt err*.txt
	-rm -rf tesslamon

.PHONY: clean all
