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

__module_id__ = '$Id$'

#
# Import system modules
#
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import gc
import sys
import time
import traceback
import types
import unittest

#
# Preserve stdout in case some test overrides it
#
STDOUT=sys.stdout

#
# Import Local modules
#
from proctorlib.trace import trace
from proctorlib import scanner

#
# Module
#
def _some_str(value):
    try:
        return str(value)
    except:
        return '<unprintable %s object>' % type(value).__name__

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
        
        STDOUT.write('\n')
        STDOUT.write("Ran %d test%s in %.3fs\n" % (run,
                                                   run == 1 and "" or "s",
                                                   elapsed_time))
        STDOUT.write('\n')

        if not self.wasSuccessful():

            #failed, errored = map(len, (self.failures, self.errors))
            failed = len(self.failures)
            errored = len(self.errors)

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

            STDOUT.write("FAILED (%s%s)\n" % (failures, errors))

        else:
            STDOUT.write("OK\n")
        return


    def startTest(self, test):
        trace.into('ProctorTestResult', 'startTest', test=test)

        unittest.TestResult.startTest(self, test)

        desc = test.id()
        progress_line = '%3d/%3d %s ...' % (self.num_tests_run,
                                            self.num_tests,
                                            desc,
                                            )
        STDOUT.write(progress_line)
        STDOUT.flush()

        self.num_tests_run += 1
        
        trace.outof()
        return

    def _showGarbage(self):
        """
        show us what's the garbage about
        """
        if gc.isenabled():
            #
            # Save the current settings
            #
            flags = gc.get_debug()
            th = gc.get_threshold()
            #sys.stderr.write("GC: Thresholds = %s\n" % str(th))
            
            try:
                #
                # Perform aggressive collection
                #
                gc.set_debug(gc.DEBUG_LEAK)
                gc.set_threshold(1, 1, 1)
                # force collection
                sys.stderr.write("GC: Collecting...\n")
                for i in range(6):
                    gc.collect()

                #
                # Remember what is garbage now
                #
                garbage = gc.garbage
            finally:
                gc.set_debug(flags)
                gc.set_threshold(*th)

            #
            # Report on current garbage
            #
            if not garbage:
                sys.stderr.write('GC: no garbage\n')
            else:
                sys.stderr.write("GC: Garbage objects:\n")
                for x in garbage:
                    for c in [ scanner.ModuleTree,
                               ]:
                        if isinstance(x, c):
                            # ignore
                            continue

                    s = str(x)
                    #if len(s) > 80: s = s[:80]
                    sys.stderr.write(str(type(x)))
                    sys.stderr.write("\n  %s\n" % s)
                
            # collect again without DEBUG_LEAK
            gc.collect()
        #else:
        #    print 'GC: disabled'
        return

    def stopTest(self, test):
        trace.into('ProctorTestResult', 'stopTest', test=test)
        
        unittest.TestResult.stopTest(self, test)

        try:
            self._showGarbage()
        except Exception, err:
            print 'GC ERROR: ', err
        
        trace.outof()
        return

    def _format_exception_only(self, etype, value, *args):
        """Format the exception part of a traceback as the output of grep.

        The arguments are the exception type and value such as given by
        sys.last_type and sys.last_value. The return value is a list of
        strings, each ending in a newline.  Normally, the list contains a
        single string; however, for SyntaxError exceptions, it contains
        several lines that (when printed) display detailed information
        about where the syntax error occurred.  The message indicating
        which exception occurred is the always last string in the list.
        """
        list = []
        if type(etype) == types.ClassType:
            stype = etype.__name__
        else:
            stype = etype

        if value is None:
            list.append('%s\n' % str(stype))
        else:
            if etype is SyntaxError:
                try:
                    msg, (filename, lineno, offset, line) = value
                except:
                    pass
                else:
                    if not filename: filename = "<string>"
                    if line is not None:
                        i = 0
                        while i < len(line) and line[i].isspace():
                            i = i+1
                        list.append('%s:%d:%s\n' % (filename, lineno, line.strip()))
                        if offset is not None:
                            s = '    '
                            for c in line[i:offset-1]:
                                if c.isspace():
                                    s = s + c
                                else:
                                    s = s + ' '
                            list.append('%s^\n' % s)
                        value = msg
            s = _some_str(value)
            if s:
                list.append('%s: %s\n' % (str(stype), s))
            else:
                list.append('%s\n' % str(stype))

        return list

    def _format_list(self, extracted_list):
        """Format a list of traceback entry tuples for printing.

        Given a list of tuples as returned by extract_tb() or
        extract_stack(), return a list of strings ready for printing.
        Each string in the resulting list corresponds to the item with the
        same index in the argument list.  Each string ends in a newline;
        the strings may contain internal newlines as well, for those items
        whose source text line is not None.
        """
        list = []
        for filename, lineno, name, line in extracted_list:
            item = '%s:%d:%s:%s\n' % (filename,lineno,line.strip(),name)
            list.append(item)
        return list

    #def _exc_info_to_string(self, err):
    #    """Converts a sys.exc_info()-style tuple of values into a string."""
    #    #err_class, err_inst, tb = err
    #    #formated_exception = self._format_list(traceback.extract_tb(tb, None))
    #    formated_exception = traceback.format_exception(*err)
    #    return ''.join(formated_exception)
    
    def addError(self, test, err):
        trace.into('TestResult', 'addError', test=test, err=err)
        unittest.TestResult.addError(self, test, err)
        STDOUT.write('ERROR in %s\n' % test.id())
        STDOUT.write(self._exc_info_to_string(err, test))
        STDOUT.write('\n')
        STDOUT.flush()
        trace.outof()
        return

    def addFailure(self, test, err):
        trace.into('TestResult', 'addFailure', test=test, err=err)
        unittest.TestResult.addFailure(self, test, err)
        STDOUT.write('FAIL in %s\n' % test.id())
        STDOUT.write(self._exc_info_to_string(err, test))
        STDOUT.write('\n')
        STDOUT.flush()
        trace.outof()
        return

    def addSuccess(self, test):
        trace.into('TestResult', 'addSuccess', test=test)

        unittest.TestResult.addSuccess(self, test)
        STDOUT.write('ok\n')
        STDOUT.flush()
        
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
        STDOUT.write('%s %s\n\n' % (self.PREFIX, message))
        STDOUT.flush()
        return
    
    def startTest(self, test):
        self._outputSeparator('Start test')
        
        unittest.TestResult.startTest(self, test)

        STDOUT.write('%s\n' % test.id())
        STDOUT.flush()

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
        STDOUT.write(progress_line)
        STDOUT.write('\n')
        
        self._outputSeparator('End progress')
        STDOUT.flush()

        return

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)

        self._outputSeparator('Start results')
        STDOUT.write('ok\n')
        self._outputSeparator('End results')
        STDOUT.flush()
        return
    
    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        STDOUT.write(self._exc_info_to_string(err, test))
        STDOUT.write('\n')

        self._outputSeparator('Start results')
        STDOUT.write('ERROR in %s\n' % test.id())
        self._outputSeparator('End results')
        STDOUT.flush()
        return

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)

        STDOUT.write(self._exc_info_to_string(err, test))

        self._outputSeparator('Start results')
        STDOUT.write('FAIL in %s\n' % test.id())
        self._outputSeparator('End results')
        STDOUT.flush()
        return

    def showSummary(self):
        self._outputSeparator('Start summary')
        elapsed_time = float(self.end_time - self.start_time)
        
        num_failures = len(self.failures)
        num_errors = len(self.errors)
        
        STDOUT.write('Failures: %d\n' % num_failures)
        STDOUT.write('Errors: %d\n' % num_errors)
        successes = (self.num_tests - (num_failures + num_errors))
        STDOUT.write('Successes: %d\n' % successes)
        STDOUT.write('Tests: %d\n' % self.num_tests_run)
        STDOUT.write('Elapsed time (sec): %.3f\n' % elapsed_time)

        if num_failures or num_errors:
            status = 'FAILED'
        else:
            status = 'OK'

        STDOUT.write('Status: %s\n' % status)
        
        self._outputSeparator('End summary')
        STDOUT.flush()
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
    
