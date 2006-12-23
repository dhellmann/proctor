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

"""Command line interface to proctor

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile$',
    'rcs_id'       : '$Id$',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'Proctor',
    'created'      : 'Wed, 19-Jun-2002 08:39:31 EDT',

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
import string
import sys
import time
import traceback
import unittest


#
# Import Local modules
#
import proctorlib
from proctorlib.trace import trace

#
# Module
#

class proctorbatch(proctorlib.CommandLineApp):
    """
    Proctor is a tool for running unit tests.  It enhances the
    existing unittest module to provide the ability to find all tests
    in a set of code, categorize them, and run some or all of them.
    Test output may be generated in a variety of formats to support
    parsing by another tool or simple, nicely formatted, reports for
    human review.
    """
    
    shortArgumentsDescription = "[<directory name> ...]"

    list_mode = 0
    list_categories_mode = 0
    run_mode = 1
    parsable_mode = 0
    coverage_filename = None
    coverage = 1
    interleaved = 0
    category = 'All'
    
    def optionHandler_list(self):
        """List tests.
        """
        self.list_mode = 1
        return

    def optionHandler_list_categories(self):
        """List test categories.
        """
        self.list_categories_mode = 1
        return

    def optionHandler_no_run(self):
        """Do not run the tests
        """
        self.run_mode = 0
        return

    def optionHandler_category(self, categoryName):
        """Run only the tests in the specified category.

        Warning: If there are no tests in a category,
        an error will not be produced.  The test suite
        will appear to be empty.
        """
        self.category = categoryName
        return

    def optionHandler_interleaved(self):
        """Interleave error and failure messages
        with the test list.
        """
        self.interleaved = 1
        return

    def optionHandler_parsable(self):
        """Format output to make it easier to parse.
        """
        self.interleaved = 1
        self.parsable_mode = 1
        return

    def optionHandler_coverage_file(self, filename):
        """Write coverage statistics to the specified file.
        """
        self.coverage_filename = filename
        return

    def optionHandler_no_coverage(self):
        """Disable coverage analysis.
        """
        self.coverage = 0
        return

    def showNode(self, node, data=None):
        num_node_tests = node.getTestSuite(0).countTestCases()
        if not num_node_tests:
            return
        node_name = node.getName()
        num_all_tests = node.getTestSuite(1).countTestCases()
        print '%s: %s/%s' % (node_name, num_node_tests, num_all_tests)
        return

    def runTests(self, module_tree):
        
        test_suite = module_tree.getTestSuite(full=1, category=self.category)
        
        verbosity = self.verboseLevel + 1
        
        if self.interleaved:
            if self.parsable_mode:
                result_factory = proctorlib.runner.ProctorParsableTestResult
            else:
                result_factory = proctorlib.runner.ProctorTestResult
                
            test_runner = proctorlib.runner.TestRunner(
                verbosity=verbosity,
                resultFactory=result_factory,
                )
        else:
            test_runner = unittest.TextTestRunner(descriptions=0,
                                                  verbosity=verbosity)

        #
        # Set up progress management info.
        #
        result = test_runner.run(test_suite)

        return result

    def _showTestInfo(self, node, data):
        if hasattr(node, '_tests'):
            for test in node._tests:
                self._showTestInfo(test, data)
        else:
            #self.statusMessage('node=%s' % node)
            #self.statusMessage('data=%s' % data)
            if self.parsable_mode:
                desc = '(%s)' % (node.shortDescription() or '')
            else:
                desc = node.shortDescription() or ''
                if desc:
                    desc = '(%s)' % desc
            id = node.id()
            print '%s %s' % (id, desc)
        return

    def listTests(self, moduleTree):
        #self.statusMessage('List here')
        #moduleTree.walk(self._showTestInfo, None)
        if self.parsable_mode:
            print '__PROCTOR__ Start list'
        suite = moduleTree.getTestSuite(1, category=self.category)
        for test in suite._tests:
            self._showTestInfo(test, None)
        success = 1
        if self.parsable_mode:
            print '__PROCTOR__ End list'
        return success

    def listCategories(self, moduleTree):
        categories = moduleTree.getTestCategories()
        categories.sort()
        for category in categories:
            print category
        return

    def getModuleTree(self, args):

        scanner = proctorlib.scanner.ModuleScanner(verboseLevel=self.verboseLevel)
        
        #
        # Handle command line arguments.  We take no options, so assume
        # everything is an argument.
        #
        if len(args) > 0:
            dirs_to_scan = args
        else:
            dirs_to_scan = ['.']
            
        for dir_to_scan in dirs_to_scan:
            scanner.scan(dir_to_scan)

        module_tree = scanner.getModuleTree()
        return module_tree
    
    def main(self, *args):

        #
        # Strip arguments from the command line, so our
        # args do not confuse another app or library.
        #
        sys.argv = [ sys.argv[0] ]

        module_tree = self.getModuleTree(args)

        #
        # If they asked for a list of the tests, print that
        # first.
        #
        if self.list_mode:
            success = self.listTests(module_tree)

        #
        # If they asked for a list of test categories,
        # print that here.
        #
        if self.list_categories_mode:
            success = self.listCategories(module_tree)

        #
        # If they asked to have tests run, do that
        # last.
        #
        if self.run_mode:
            
            #
            # Possibly override the coverage filename
            #
            if self.coverage_filename:
                import os
                os.environ['COVERAGE_FILE'] = self.coverage_filename
                
            if self.coverage:
                #
                # Wait to do the import of this module until right here,
                # in case the filename was specified via the command line.
                # An API to the coverage module would be nice...
                #
                from proctorlib import coverage
                #
                # Start code coverage counter
                #
                coverage.start()
                
            #
            # Get the module tree.  This needs to be done *after*
            # coverage monitoring is started so we monitor those
            # modules, too.
            #
            module_tree = self.getModuleTree(args)
            
            #
            # Run the tests
            #
            result = self.runTests(module_tree)

            if self.coverage:
                #
                # Stop coverage counter and save its results
                #
                coverage.stop()
                coverage.the_coverage.save()
                
            #
            # Report our success/failure
            #
            success = result.wasSuccessful()

        return success

    

