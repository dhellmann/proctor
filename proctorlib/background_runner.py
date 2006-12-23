#
# $Id$
#
# Copyright 2003 Racemi, Inc.
#

"""Background test runner.

    Spawns off a 'proctorbatch' job to run the tests based on its
    arguments, and returns a result set with the test results.

"""

#
# Import system modules
#
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import popen2
import re

#
# Import Local modules
#


#
# Module
#

class TestInfo:
    "Collect information about the test."

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.setStatus('NOT RUN')
        self.output = ''
        return

    def setStatus(self, status):
        "Set the status of the test."
        self.status = status
        return
    
    def feed(self, line):
        "Feed text to the test output buffer."
        self.output = self.output + line
        return

    def __str__(self):
        return '%s - %s\n%s\n' % (self.name, self.status, self.output)


class BackgroundTestRunner:
    """Background test runner.

        Spawns off a 'proctorbatch' job to run the tests based on its
        arguments, and returns a result set with the test results.

    """


    def __init__(self,
                 inputPaths=[],
                 progressFunc=None,
                 runTests=1,
                 appName='proctorbatch',
                 appDefaultArgs='--parsable --no-coverage --list',
                 ):
        """Constructor

        Parameters

          runTests=1 -- Boolean controlling whether tests are actually
          run.  If false, a list of tests is made available but they
          are not executed.
          
        """   
        self.input_paths = inputPaths
        self.progress_func = progressFunc
        self.run_tests = runTests
        self.app_name = appName
        self.app_default_args = appDefaultArgs

        self.test_results = {}
        self.test_names = []
        self.mode = 'not_running'
        return

    def getCommand(self):
        "Returns a command string to be used for this runner."
        if self.run_tests:
            run_arg = ''
        else:
            run_arg = '--no-run'

        if self.input_paths:
            input_names = ' '.join(self.input_paths)
        else:
            input_names = ''
            
        command = '%s %s %s %s' % (self.app_name,
                                   self.app_default_args,
                                   run_arg,
                                   input_names,
                                   )
        return command
    
    def start(self):
        "Begin the tests running."
        command = self.getCommand()
        self.pipe = popen2.Popen4(command)
        self._results_buffer = StringIO()
        return

    TRANSITIONS = [
        (re.compile('^__PROCTOR__ Start list'), 'getting_list'),
        (re.compile('^__PROCTOR__ End list'), 'not_running'),
        (re.compile('^__PROCTOR__ Start run'), 'running'),
        (re.compile('^__PROCTOR__ End run'), 'not_running'),
        (re.compile('^__PROCTOR__ Start test'), 'in_test'),
        (re.compile('^__PROCTOR__ End test'), 'running'),
        (re.compile('^__PROCTOR__ Start results'), 'test_results'),
        (re.compile('^__PROCTOR__ End results'), 'in_test'),
        (re.compile('^__PROCTOR__ Start progress'), 'progress'),
        (re.compile('^__PROCTOR__ End progress'), 'running'),
        ]
        
    def isStillRunning(self):
        "Return true value if the tests are still running, or false if they are done."
        poll_results = self.pipe.poll()

        #
        # Accumulate the entire output buffer
        #
        incremental_output = self.pipe.fromchild.readline()
        self._results_buffer.write(incremental_output)

        #
        # Do we need to change modes?
        #
        mode_changed = 0
        for pattern, new_mode in self.TRANSITIONS:
            if pattern.match(incremental_output):
                self.mode = new_mode
                mode_changed = 1
                break

        #
        # Deal with this individual line
        # using the current mode.
        #
        if not mode_changed:
            handler_name = 'lineHandler_%s' % self.mode
            handler = getattr(self, handler_name)
            handler(incremental_output)
        
        return (poll_results == -1)

    def lineHandler_not_running(self, line):
        "No-op"
        return
    
    def lineHandler_progress(self, line):
        "No-op"
        line = line.strip()
        if line:
            if self.progress_func:
                parts = line.split('/')
                if len(parts) == 2:
                    current, total = parts
                    current = int(current)
                    total = int(total)
                    self.progress_func(current, total)
        return

    def lineHandler_getting_list(self, line):
        "Handle one test name in the list."
        line_parts = line.split(' ')
        test_name = line_parts[0]
        
        self.test_names.append(test_name)

        description = ' '.join(line_parts[1:]).strip()
        if description and description[0] == '(':
            description = description[1:]
        if description and description[-1] == '>':
            description = description[:-1]
        
        test_info = TestInfo(test_name, description)
        self.test_results[test_name] = test_info
        return

    def lineHandler_running(self, line):
        "No-op"
        #
        # (Re)Set the current test name
        #
        self._current_test_name = None
        
        line = line.strip()
        return

    def lineHandler_in_test(self, line):
        "Add line to the output buffer for the individual test."
        if self._current_test_name is None:
            line = line.strip()
            if line:
                # This is the test name.
                self._current_test_name = line
        else:
            #
            # We know the test, so just add
            # to its output buffer.
            #
            test_info = self.test_results[self._current_test_name]
            test_info.feed(line)
        return

    def lineHandler_test_results(self, line):
        "Set the result for the test."
        line = line.strip()
        if line:
            test_info = self.test_results[self._current_test_name]
            test_info.setStatus(line.strip())
        return
    
    def end(self):
        "End the tests running."
        return
        


if __name__ == '__main__':
    import time

    def progress_handler(current, total):
        print 'CURRENT_PROGRESS:', ((current * 1.0 / total) * 100)
    
    btr = BackgroundTestRunner(['.'],
                               progressFunc=progress_handler,
                               runTests=1,
                               appName='./proctorbatch',
                               )
    btr.start()
    while btr.isStillRunning():
        pass
    btr.end()

    for test_name in btr.test_names:
        print btr.test_results[test_name]
