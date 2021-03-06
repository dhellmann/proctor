#!/usr/bin/env python
#
# Copyright 2007 Doug Hellmann.
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

"""CLI app to filter test output to show only the tests which did not pass.

"""

__module_id__ = "$Id$"

#
# Import system modules
#

#
# Import Local modules
#
import proctorlib

#
# Module
#

class SectionStack:

    def __init__(self):
        self.stack = []
        return

    def top(self):
        if not self.stack:
            return None
        return self.stack[-1]

    def push(self, value):
        self.stack.append(value)
        return

    def pop(self):
        return self.stack.pop()

class TestResult:
    """Result of a single test, parsed from the output of a test run.
    """

    OK = 'ok'
    ERROR = 'ERROR'
    FAIL = 'FAIL'

    def __init__(self, name, output, result):
        self.name = name
        self.output = output
        self.result = result
        self.status = result.split(' ')[0]
        return

    def passed(self):
        "Return boolean indicating whether or not the test passed."
        return (self.status == self.OK)

    def __str__(self):
        return '%s: %s' % (self.name, self.status)

class ResultFactory:
    """Parse a sequence of lines to create TestResult instances.

    The callback argument must be a callable object which accepts a
    single positional argument.  Each time a new test result is
    completely parsed, the callback will be invoked with a TestResult
    instance containing the information about that test.
    """

    def __init__(self, callback):
        self.current_result = {}
        self.section_stack = SectionStack()
        self.callback = callback
        return

    def feed(self, text):
        "Add one line of input to the parser."
        lines = text.split('\n')
        for line in lines:
            if line:
                self.feedLine(line)
        return

    def feedLine(self, line):
        line = line.rstrip()

        if line.startswith(proctorlib.runner.ProctorParsableTestResult.PREFIX):
            parts = line.split(' ')
            action = parts[1]
            section = parts[2]
            if action == 'Start':
                self.section_stack.push(section)
            elif action == 'End' and self.section_stack.top() == section:
                ended = self.section_stack.pop()
                if ended == 'test':
                    # We have everything about the test
                    name = self.current_result['test'][0] # first line of test body is name
                    output = '\n'.join(self.current_result['test'])
                    result = '\n'.join(self.current_result['results'])
                    new_result = TestResult(name, output, result)
                    self.callback(new_result)
                    self.current_result = {}
            else:
                raise ValueError('Unrecognized action "%s"' % action)
        else:
            self.current_result.setdefault(self.section_stack.top(), []).append(line)
        return
