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

%.sh:
	cat templates/script.sh.txt > $@
	chmod +x $@

clean :
	rm -rf docs
