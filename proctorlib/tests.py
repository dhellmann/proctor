#!/usr/bin/env python
#
# $Id$
#
# Copyright 2002 Doug Hellmann.
#
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Doug
# Hellmann not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

"""Example tests to illustrate how proctor works.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile$',
    'rcs_id'       : '$Id$',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'Proctor',
    'created'      : 'Sun, 16-Jun-2002 10:28:10 EDT',

    #
    #  Current Information
    #
    'author'       : '$Author$',
    'version'      : '$Revision$',
    'date'         : '$Date$',
}
try:
    __version__ = __rcs_info__['version'].split(' ')[1]
except:
    __version__ = '0.0'

#
# Import system modules
#
import sys
import time
import unittest

#
# Import Local modules
#
from proctorlib import importcount

#
# Module
#

importcount._import_count += 1

class TestImportCount(unittest.TestCase):

    def testImportedOnlyOnce(self):
        from proctorlib import importcount
        self.failUnlessEqual(importcount._import_count,
                             1,
                             )
        return

class ExampleTestCase(unittest.TestCase):

    do_sleep = 0

    def test00(self):
        sys.stdout.write('stdout\n')
        sys.stderr.write('and stderr\n')
        return

    def test01(self):
        if self.do_sleep: time.sleep(1)
        return

    def test02(self):
        if self.do_sleep: time.sleep(2)
        return

    def test03Failure(self):
        if self.do_sleep: time.sleep(3)
        self.fail('This test always fails.')
        return

    def test04Error(self):
        if self.do_sleep: time.sleep(4)
        foo()
        return
    
    def test05(self):
        return

    def test06(self):
        if self.do_sleep: time.sleep(1)
        return

    def test07(self):
        if self.do_sleep: time.sleep(2)
        return

    def test08Failure(self):
        if self.do_sleep: time.sleep(3)
        self.fail('This test always fails.')
        return

    def test09Error(self):
        if self.do_sleep: time.sleep(4)
        foo()
        return

    def test10(self):
        return

    def test11(self):
        if self.do_sleep: time.sleep(1)
        return

    def test12(self):
        if self.do_sleep: time.sleep(2)
        return

    def test13Failure(self):
        if self.do_sleep: time.sleep(3)
        self.fail('This test always fails.')
        return

    def test14Error(self):
        if self.do_sleep: time.sleep(4)
        foo()
        return
    
    def test15(self):
        return

    def test16(self):
        if self.do_sleep: time.sleep(1)
        return

    def test17(self):
        if self.do_sleep: time.sleep(2)
        return

    def test18Failure(self):
        if self.do_sleep: time.sleep(3)
        self.fail('This test always fails.')
        return

    def test19Error(self):
        if self.do_sleep: time.sleep(4)
        foo()
        return
    
    def test20(self):
        return

    def test21(self):
        if self.do_sleep: time.sleep(1)
        return

    def test22(self):
        if self.do_sleep: time.sleep(2)
        return

    def test23Failure(self):
        if self.do_sleep: time.sleep(3)
        self.fail('This test always fails.')
        return

    def test24Error(self):
        if self.do_sleep: time.sleep(4)
        foo()
        return
    
    def test25(self):
        return

    def test26(self):
        if self.do_sleep: time.sleep(1)
        return

    def test27(self):
        if self.do_sleep: time.sleep(2)
        return

    def test28Failure(self):
        if self.do_sleep: time.sleep(3)
        self.fail('This test always fails.')
        return

