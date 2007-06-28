#!/usr/bin/env python
#
# $Id$
#
# Copyright 2001 Doug Hellmann.
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

"""A debugging trace module.

  This debugging trace module makes it easier to follow nested calls
  in output by varying the indention level for log messages.  The
  caller can simply trace 'into()' a new level when control passes
  into a function call, 'write()' debug messages at appropriate spots
  in the function, then call 'outof()' when returning from the
  function.

  The debug level is set via the environment variable 'TRACE_LEVEL'.
  Level '0' or no value specified results in no output.  Positive
  integer values are used to control the verbosity of the output with
  higher numbers resulting in more output messages.

"""

__module_id__ = '$Id$'

#
# Import system modules
#
import os
import sys
import unittest

#
# Import Local modules
#

#
# Module
#


class DebugTracer:

    NO_RETURN_VALUE_SPECIFIED='No return value specified.'

    def __init__(self,
                 outputStream=sys.stdout,
                 indentBy='  ',
                 maxOutputLevel=1,
                 startLevel=0,
                 tabSize=2):
        self.setOutputStream(outputStream)
        self.level = startLevel
        self.stack = ()
        self.setIndentBy(indentBy)
        self.max_output_level = maxOutputLevel
        self.setTabSize(tabSize)
        return

    def setOutputStream(self, outputStream):
        self.output = outputStream
        return

    def setIndentBy(self, indentBy):
        self.indent_by = indentBy
        return

    def setTabSize(self, tabSize):
        self.tab_size = tabSize
        return
    
    def setVerbosity(self, level):
        self.max_output_level = level
        return

    def getIndent(self):
        return self.indent_by * self.level

    def pushLevel(self, newStackTop):
        self.level = self.level + 1
        self.stack = ( newStackTop, self.stack )
        return

    def popLevel(self):
        self.level = self.level - 1
        if self.stack:
            popped, self.stack = self.stack
        else:
            popped = ()
        return popped

    def checkOutputLevel(self, outputLevel):
        return self.max_output_level >= outputLevel

    ###

    def into(self, className, functionName, outputLevel=1, **params):
        """Enter a new debug trace level.
        
        Parameters

            'className' -- Name of the class.

            'functionName' -- The name of the function/method.

            'outputLevel=1' -- The debug level where this message should be printed.

            '**params' -- Parameters sent to the function.
        
        """
        if self.checkOutputLevel(outputLevel):
            self.write('%s::%s (' % (className, functionName), outputLevel=outputLevel)
            params = params.items()
            params.sort()
            tab = self.indent_by * self.tab_size
            for name, value in params:
                self.write('%s%s=%s, ' % ( tab,
                                           name,
                                           repr(value),
                                           ),
                           outputLevel=outputLevel,
                           )
            self.write('%s) {' % tab, outputLevel=outputLevel)
            self.pushLevel((className, functionName))
        return

    def callerParent(self, outputLevel=1):
        if self.checkOutputLevel(outputLevel):
            if not self.stack:
                self.write('ERROR: trace.callerParent called when no stack present\n',
                           outputLevel=outputLevel)
            if len(self.stack) < 2:
                parent = 'None'
            else:
                try:
                    parent = '%s::%s' % self.stack[1][0]
                except:
                    parent = str(self.stack[1])

            #self.output.write('Called by: %s\n' % parent)
            self.write('Called by: %s\n' % str(self.stack), outputLevel=outputLevel)
        return

    def write(self, message, outputLevel=1, indent=1, **vars):
        if self.checkOutputLevel(outputLevel):
            
            if indent:
                prefix = self.getIndent()
            else:
                prefix = ''
                
            self.output.write('%s%s\n' % (prefix, message))
            
            if vars.items():
                vars = vars.items()
                vars.sort()
                tab = self.indent_by * self.tab_size
                for name, value in vars:
                    self.output.write('%s%s%s=%s\n' % (prefix,
                                                     tab,
                                                     name,
                                                     repr(value),
                                                     )
                                      )
                
        return

    def writeVar(self, outputLevel=1, **variables):
        if self.checkOutputLevel(outputLevel):
            variables = variables.items()
            variables.sort()
            for name, value in variables:
                self.write('%s=%s' % (name, repr(value)), outputLevel=outputLevel)
        return

    def outof(self, returnValue=None, outputLevel=1):
        """Exit the current debug trace level.
        
            Parameters

              'returnValue' -- Optional argument indicating
                               the value returned from the function.
        """
        if self.checkOutputLevel(outputLevel):
            self.popLevel()
            self.write('} %s' % repr(returnValue), outputLevel=outputLevel)
        return returnValue

    def showTraceback(self, outputLevel=1):
        """Print the traceback for the current exception.
        """
        if self.checkOutputLevel(outputLevel):
            import traceback
            traceback.print_exc()
        return


trace=DebugTracer(maxOutputLevel=int(os.environ.get('TRACE_LEVEL', 0)))
into=trace.into
outof=trace.outof
write=trace.outof


####################################################################################


class TraceUnitTest(unittest.TestCase):

    def testTrace(self):
        from cStringIO import StringIO
        buffer = StringIO()
        trace = DebugTracer(outputStream=buffer)
        trace.callerParent()
        trace.into('__main__', 'topLevel', a='a', b='b')
        trace.callerParent()
        trace.write('hi there')
        trace.into('secondary', 'secondLevel', c='C', d='D')
        trace.write('inside second level')
        trace.callerParent()
        trace.outof()
        trace.outof('string returned')
        expected_value = """ERROR: trace.callerParent called when no stack present

Called by: ()

__main__::topLevel (
    a='a', 
    b='b', 
    ) {
  Called by: (('__main__', 'topLevel'), ())

  hi there
  secondary::secondLevel (
      c='C', 
      d='D', 
      ) {
    inside second level
    Called by: (('secondary', 'secondLevel'), (('__main__', 'topLevel'), ()))

  } None
} 'string returned'
"""
        actual_output = buffer.getvalue()
        assert actual_output == expected_value, \
               'Trace generated unexpected output [%s].' % actual_output
        return

    
