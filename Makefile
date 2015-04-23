docdir = docs
docs = $(patsubst %.sh,$(docdir)/%.txt,$(wildcard *.sh))
utildocs = $(patsubst %.sh,$(docdir)/%.txt,$(wildcard util/*.sh))
bash = /bin/bash

all : docdirs docs utildocs

docs : $(docs) 
	
utildocs : $(utildocs)

docdirs: docs/ docs/util/

docs/%.txt : %.sh 
	$(bash) $< > $@ || true

docs/util/%.txt : util/%.sh
	cat $< | grep '^#' | grep -v '#!' | sed -r 's/^# ?//' > $@

docs/ docs/util/: 
	mkdir -p $@

clean :
	rm -rf docs
