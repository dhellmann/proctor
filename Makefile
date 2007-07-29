#
# $Id$
#

SVNHOME=$(shell svn info | grep "^URL" | cut -f2- -d:)
PROJECT=Proctor
VERSION=$(shell basename $(SVNHOME))
RELEASE=$(PROJECT)-$(VERSION)

package: setup.py index.html
	python setup.py sdist --force-manifest

register: setup.py
	python setup.py register

%: %.in
	rm -f $@
	cat $< | sed 's/VERSION/$(VERSION)/g' > $@
	chmod -w $@

tags:
	find . -name '*.py' | etags -l auto --regex='/[ \t]*\def[ \t]+\([^ :(\t]+\)/\1/' -
