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
import fileinput

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
        

class proctorfilter(proctorlib.CommandLineApp):
    """
    proctorfilter reads output created by proctorbatch with the
    --parsable option and prints a list of the tests which did not
    pass.
    """
    
    shortArgumentsDescription = "[<log file name> ...]"

    def main(self, *args):
        section_stack = SectionStack()

        for line in fileinput.input(args):
            line = line.strip()
            if line.startswith(proctorlib.runner.ProctorParsableTestResult.PREFIX):
                parts = line.split(' ')
                action = parts[1]
                section = parts[2]
                if action == 'Start':
                    section_stack.push(section)
                elif action == 'End' and section_stack.top() == section:
                    section_stack.pop()
                else:
                    raise ValueError('Unrecognized action "%s"' % action)
            elif section_stack.top() == 'results':
                if not line.startswith('ok'):
                    print line
                
        return 0

    

