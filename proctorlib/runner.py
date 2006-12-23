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

"""Test runner.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile$',
    'rcs_id'       : '$Id$',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'Proctor',
    'created'      : 'Sun, 16-Jun-2002 10:51:33 EDT',

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
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import sys
import time
import traceback
import unittest

#
# Import Local modules
#
from proctorlib.trace import trace

#
# Module
#

class ProctorTestResult(unittest.TestResult):

    def __init__(self, testSuite, verbosity):
        trace.into('ProctorTestResult', '__init__')
        
        self.num_tests = testSuite.countTestCases()
        self.num_tests_run = 0
        self.verbosity = verbosity
        
        unittest.TestResult.__init__(self)
        
        trace.outof()
        return
    
    def startRun(self):
        self.start_time = time.time()
        return
    
    def endRun(self):
        self.end_time = time.time()
        return

    def showSummary(self):
        run = self.num_tests_run
        
        elapsed_time = float(self.end_time - self.start_time)
        
        print
        print "Ran %d test%s in %.3fs" % (run,
                                          run == 1 and "" or "s",
                                          elapsed_time)
        print

        if not self.wasSuccessful():

            failed, errored = map(len, (self.failures, self.errors))

            if failed:
                failures = "failures=%d" % failed
            else:
                failures = ''

            if errored:
                if failed:
                    errors = ", errors=%d" % errored
                else:
                    errors = "errors=%d" % errored
            else:
                errors = ''

            print "FAILED (%s%s)" % (failures, errors)

        else:
            print "OK"
        return


    def startTest(self, test):
        trace.into('ProctorTestResult', 'startTest', test=test)

        unittest.TestResult.startTest(self, test)

        desc = test.shortDescription() or str(test)
        progress_line = '%3d/%3d %s ...' % (self.num_tests_run,
                                            self.num_tests,
                                            desc,
                                            )
        print progress_line,

        self.num_tests_run += 1
        
        trace.outof()
        return

    def stopTest(self, test):
        trace.into('ProctorTestResult', 'stopTest', test=test)

        unittest.TestResult.stopTest(self, test)
        
        trace.outof()
        return

    def _exc_info_to_string(self, err):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        return string.join(apply(traceback.format_exception, err), '')
    
    def addError(self, test, err):
        trace.into('TestResult', 'addError', test=test, err=err)
        unittest.TestResult.addError(self, test, err)
        print 'ERROR'
        print self._exc_info_to_string(err)
        trace.outof()
        return

    def addFailure(self, test, err):
        trace.into('TestResult', 'addFailure', test=test, err=err)
        unittest.TestResult.addFailure(self, test, err)
        print 'FAIL'
        print self._exc_info_to_string(err)
        print
        trace.outof()
        return

    def addSuccess(self, test):
        trace.into('TestResult', 'addSuccess', test=test)

        unittest.TestResult.addSuccess(self, test)
        print 'ok'
        
        trace.outof()
        return


class ProctorParsableTestResult(ProctorTestResult):
    "Test results displayed in parsable fashion."

    PREFIX = '__PROCTOR__'
    
    def __init__(self, testSuite, verbosity):
        ProctorTestResult.__init__(self, testSuite, verbosity)
        return

    def startRun(self):
        self._outputSeparator('Start run')
        ProctorTestResult.startRun(self)
        return
    
    def endRun(self):
        self._outputSeparator('End run')
        ProctorTestResult.endRun(self)
        return

    def _outputSeparator(self, message):
        print '%s %s' % (self.PREFIX, message)
        print
        return
    
    def startTest(self, test):
        self._outputSeparator('Start test')
        
        unittest.TestResult.startTest(self, test)

        print test.id()

        self.num_tests_run += 1
        
        trace.outof()
        return

    def stopTest(self, test):
        ProctorTestResult.stopTest(self, test)
        self._outputSeparator('End test')
        #
        # Show progress
        #
        self._outputSeparator('Start progress')
        progress_line = '%3d/%3d' % (self.num_tests_run,
                                     self.num_tests,
                                     )
        print progress_line
        self._outputSeparator('End progress')

        return

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)

        self._outputSeparator('Start results')
        print 'ok'
        self._outputSeparator('End results')
        return
    
    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        print self._exc_info_to_string(err)

        self._outputSeparator('Start results')
        print 'ERROR'
        self._outputSeparator('End results')
        return

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)

        print self._exc_info_to_string(err)

        self._outputSeparator('Start results')
        print 'FAIL'
        self._outputSeparator('End results')
        return

    def showSummary(self):
        self._outputSeparator('Start summary')
        elapsed_time = float(self.end_time - self.start_time)
        
        num_failures = len(self.failures)
        num_errors = len(self.errors)
        
        print 'Failures: %d' % num_failures
        print 'Errors: %d' % num_errors
        successes = (self.num_tests - (num_failures + num_errors))
        print 'Successes: %d' % successes
        print 'Tests: %d' % self.num_tests_run
        print 'Elapsed time (sec): %.3f' % elapsed_time

        if num_failures or num_errors:
            status = 'FAILED'
        else:
            status = 'OK'

        print 'Status: %s' % status
        
        self._outputSeparator('End summary')
        return
    
    
        

class TestRunner:

    def __init__(self,
                 verbosity=1,
                 resultFactory=ProctorTestResult,
                 ):
        self.verbosity = verbosity
        self.result_factory = resultFactory
        return

    def _makeResult(self, test):
        return self.result_factory(test, self.verbosity)
    
    def run(self, test):
        result = self._makeResult(test)

        result.startRun()

        test(result)

        result.endRun()
        result.showSummary()
        return result
    
