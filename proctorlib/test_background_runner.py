#
# $Id$
#
# Copyright 2003 Racemi, Inc.
#

"""Tests for background_runner.py

"""

#
# Import system modules
#
import unittest


#
# Import Local modules
#
from proctorlib.background_runner import BackgroundTestRunner

#
# Module
#

class BackgroundTestRunnerCommandTest(unittest.TestCase):

    def testWithoutRunning(self):
        btr = BackgroundTestRunner(runTests=0, inputPaths=['foo'])
        command = btr.getCommand()
        self.failUnlessEqual(
            command,
            'proctorbatch --parsable --no-coverage --list --no-run foo'
            )
        return

    def testWithRunning(self):
        btr = BackgroundTestRunner(inputPaths=['foo'])
        command = btr.getCommand()
        self.failUnlessEqual(
            command,
            'proctorbatch --parsable --no-coverage --list  foo'
            )
        return

    def testWithoutRunningMultiplePaths(self):
        btr = BackgroundTestRunner(runTests=0, inputPaths=['foo', 'bar'])
        command = btr.getCommand()
        self.failUnlessEqual(
            command,
            'proctorbatch --parsable --no-coverage --list --no-run foo bar'
            )
        return

    def testWithRunningMultiplePaths(self):
        btr = BackgroundTestRunner(inputPaths=['foo', 'bar'])
        command = btr.getCommand()
        self.failUnlessEqual(
            command,
            'proctorbatch --parsable --no-coverage --list  foo bar'
            )
        return


if __name__ == '__main__':
    unittest.main()
