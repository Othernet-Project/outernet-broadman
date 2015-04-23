docdir = docs
docs = $(patsubst %.sh,$(docdir)/%.txt,$(wildcard *.sh))
utildocs = $(patsubst %.sh,$(docdir)/%.txt,$(wildcard util/*.sh))
bash = /bin/bash

all : docdirs docs utildocs

docs : $(docs) 
	
utildocs : $(utildocs)

docs/%.txt : %.sh 
	$(bash) $< > $@ || true

docs/util/%.txt : util/%.sh
	cat $< | grep '^#' | grep -v '#!' | sed -r 's/^# ?//' > $@

docdirs: 
	mkdir -p $(docdir)
	mkdir -p $(docdir)/util

clean :
	rm -rf docs
