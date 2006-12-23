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

"""Tests for the Proctor test scanner.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile$',
    'rcs_id'       : '$Id$',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'Proctor',
    'created'      : 'Tue, 03-Dec-2002 09:02:09 EST',

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
import unittest

#
# Import Local modules
#
import os
import proctorlib.scanner

#
# Module
#
CATEGORIZED_TESTS = 'CategorizedTests'
CATEGORY_ONE = 'CategoryOne'
CATEGORY_TWO = 'CategoryTwo'
    
class CategoryOneTests(unittest.TestCase):

    PROCTOR_TEST_CATEGORIES = ( CATEGORIZED_TESTS,
                                CATEGORY_ONE,
                                )

    def testCategoryOne(self):
        return
    
class CategoryTwoTests(unittest.TestCase):

    PROCTOR_TEST_CATEGORIES = ( CATEGORIZED_TESTS,
                                CATEGORY_TWO,
                                )

    def testCategoryTwo(self):
        return
    
class UncategorizedTests(unittest.TestCase):

    def testUncategorized(self):
        return
    

class ScannerCategoryTest(unittest.TestCase):

    def setUp(self):
        self.scanner = proctorlib.scanner.ModuleScanner()
        self.scanner.scan(os.curdir)
        return

    def testFindCategoryOne(self):
        test_suite = self.scanner.getTestSuite(category=CATEGORY_ONE)
        self.failUnlessEqual(test_suite.countTestCases(), 1)
        return
    
    def testFindCategoryTwo(self):
        test_suite = self.scanner.getTestSuite(category=CATEGORY_TWO)
        self.failUnlessEqual(test_suite.countTestCases(), 1)
        return
    
    def testFindCategorizedTests(self):
        test_suite = self.scanner.getTestSuite(category=CATEGORIZED_TESTS)
        self.failUnlessEqual(test_suite.countTestCases(), 2)
        return
    
    def testFindUncategorizedTests(self):
        test_suite = self.scanner.getTestSuite(category='Unspecified')
        self.failUnless(test_suite.countTestCases())
        return
    
    def testFindAllTests(self):
        test_suite = self.scanner.getTestSuite(category='All')
        self.failUnless(test_suite.countTestCases())
        return
    
    def testFindNoSuchCategory(self):
        test_suite = self.scanner.getTestSuite(category='NoSuchCategory')
        self.failUnlessEqual(test_suite.countTestCases(), 0)
        return

if __name__ == '__main__':
    unittest.main()
