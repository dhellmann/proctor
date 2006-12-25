#
# $Id$
#

#
# 0. (tag work directory)
# 1. gmake dist REV=rX_Y
# 2. gmake ftp_install REV=rX_Y
# 3. (create new release, add file)
#

SVNHOME=$(shell svn info | grep "^URL" | cut -f2- -d:)
PROJECT=Proctor
VERSION=$(shell basename $(SVNHOME))
RELEASE=$(PROJECT)-$(VERSION)

package: setup.py index.html
	python setup.py sdist --force-manifest

%: %.in
	cat $< | sed 's/VERSION/$(VERSION)/g' > $@

tags:
	find . -name '*.py' | etags -l auto --regex='/[ \t]*\def[ \t]+\([^ :(\t]+\)/\1/' -
