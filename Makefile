#
# $Id$
#

SVNHOME=$(shell svn info | grep "^URL" | cut -f2- -d:)
PROJECT=Proctor
VERSION=$(shell basename $(SVNHOME))
RELEASE=$(PROJECT)-$(VERSION)

package:
	rm -f setup.py index.html
	$(MAKE) setup.py index.html
	python setup.py sdist --force-manifest
	mv dist/*.gz ~/Desktop/

register: setup.py
	python setup.py register

%: %.in
	cat $< | sed 's/VERSION/$(VERSION)/g' > $@
	chmod -w $@

tags:
	find . -name '*.py' | etags -l auto --regex='/[ \t]*\def[ \t]+\([^ :(\t]+\)/\1/' -
