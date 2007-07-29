#!/usr/bin/env python
#
# $Id$
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

"""GUI for displaying and running tests.

"""

__module_id__ = '$Id$'

#
# Import system modules
#
import os
import Pmw
import PmwContribD
from Tkinter import *
import tkFileDialog

#
# Import Local modules
#
from proctorlib.runner import TestRunner, ProctorTestResult
from proctorlib.scanner import ModuleScanner
from proctorlib.trace import trace
from proctorlib.icon import TestIcon
from proctorlib.prefs import ProctorPrefs

#
# Module
#

class ProctorGUI(PmwContribD.GuiAppD):

    appversion = '0.1'
    appname = 'Proctor'
    contactname='Doug Hellmann'
    copyrightname=contactname
    copyright='Copyright %s 2002\nAll rights reserved.' % copyrightname
    contactphone=''
    contactemail='doug@hellfly.net'
    
    usebuttonbox = 1

    user_preferences = ProctorPrefs()

    ##
    ## INIT APPLICATION
    ##
    
    def appInit(self):
        """Pre-GUI application initialization.
        """
        self.state = 'idle'
        self.tests = []
        self.scanner = None
        self.test_buttons = {}
        #
        # Variable to hold reference to directory with input modules
        #
        self.scan_directory = StringVar()
        self.scan_directory_parent = os.getcwd()
        self.scan_directory.set('.')
        #self.scan_directory.set(os.getcwd())
        self.result = None
        return

    ##
    ## CONSTRUCT UI
    ##

    def _createTestButtonArea(self, parent):
        """Create the GUI area to hold the test buttons.
        """
        frame = self.createcomponent('testbuttonframe', (), None,
                                     Frame,
                                     (parent,),
                                     relief=SUNKEN,
                                     bd=2)
        #
        # Widgets to show and change the directory to scan
        #
        frame2 = self.createcomponent('scanndirectoryframe', (), None,
                                      Frame,
                                      (frame,),
                                      relief=FLAT,
                                      bd=2)
        self.cwd_label = self.createcomponent('cwdlabel', (), None,
                                              Label,
                                              (frame2,),
                                              textvariable=self.scan_directory,
                                              relief=FLAT,
                                              justify=LEFT,
                                              anchor='w',
                                              )
        self.cwd_label.pack(side=LEFT,
                            expand=YES,
                            fill=X,
                            )
        btn = self.createcomponent('changescandirectorybtn', (), None,
                                   Button,
                                   (frame2,),
                                   command=self.changeScanDirectoryCB,
                                   text='Change...',
                                   )
        btn.pack(side=LEFT,
                 expand=NO,
                 fill=X,
                 )
        frame2.pack(side=TOP,
                    expand=YES,
                    fill=X,
                    )
        #
        # Create the action buttons
        #
        self.createcomponent('testcanvas', (), None,
                             Pmw.ScrolledCanvas,
                             (frame,),
                             canvas_background=self.user_preferences['background'],
                             canvasmargin=self.user_preferences['spacing'],
                             usehullsize=1,
                             hull_height=5,
                             )
        self.canvas = self.component('testcanvas').component('canvas')
        self.idleWidgets.append(self.canvas)
        self.component('testcanvas').pack(side=TOP,
                                          expand=YES,
                                          fill=BOTH,
                                          )
        
        frame.pack(side=TOP,
                   expand=NO,
                   fill=X,
                   padx=self['padx'],
                   pady=self['pady'],
                   )
        #
        # Create a button for each test
        #
        self.configureTestIconsFromPrefs()
        self._updateTestButtons()
        #
        # Register the variable callback so that the buttons are updated
        # automatically later.  We do not do this earlier to avoid
        # recursive loops.
        #
        #self.scan_directory.trace_variable('w', self._changeScanDirectoryVariableCB)
        return
    
    def createInterface(self):
        """Construct the GUI.
        """
        PmwContribD.GuiAppD.createInterface(self)
        #
        # Widget to hold output and test buttons
        #
        main = self.createcomponent('main', (), None,
                                    Frame,
                                    (self.interior(),),
                                    )
        #
        # Make test buttons
        #
        self._createTestButtonArea(main)
        #
        # Make output display
        #
        self.output_text = self.createcomponent('outputscrolledtext', (), None,
                                                Pmw.ScrolledText,
                                                (main,),
                                                text_height=10,
                                                text_width=20,
                                                labelpos='nw',
                                                text_state='disabled',
                                                text_wrap='none',
                                                )
        self.output_text.pack(side=TOP,
                              expand=YES,
                              fill=BOTH,
                              padx=self['padx'],
                              pady=self['pady'],
                              )
        self.busyWidgets.append(self.output_text.component('text'))
        #
        # Done with main pane
        #
        main.pack(side=TOP,
                  expand=YES,
                  fill=BOTH,
                  padx=self['padx'],
                  pady=self['pady'],
                  )
        #
        # Change the app progress meter to not include the time
        #
        self.component('progressmeter').configure(
            indicatorformat='%(progress)s/%(finishvalue)s (%(percentdone)s %%)',
            )
        #
        # Make a "Go" button
        #
        self.go_button = self.buttonAdd('Go', command=self.runTestsCB,
                                        helpMessage='Run tests',
                                        )
        self.buttonBox().setdefault(0)
        self.rescan_button = self.buttonAdd('Rescan', command=self.rescanTestsCB,
                                            helpMessage='Look for tests',
                                            )
        self.reset_button = self.buttonAdd('Reset', command=self.resetTestsCB,
                                           helpMessage='Clear test results',
                                           )
        self.stop_button = self.buttonAdd('Stop', command=self.stopTestsCB,
                                          helpMessage='Stop the current test run',
                                          state='disabled',
                                          )
        
        return

    ##
    ## GUI CALLBACKS
    ##

    def savePrefsCB(self, *args):
        trace.into('ProctorGUI', 'savePrefsCB', arguments=args)
        self.component('testcanvas').configure(
            canvas_background=self.user_preferences['background'],
            )
        self.configureTestIconsFromPrefs()
        trace.outof()
        return

    def configureTestIconsFromPrefs(self):
        #
        # Update the class color definitions
        #
        for name in TestIcon.COLORS.keys():
            TestIcon.COLORS[name] = self.user_preferences[name]
        #
        # Update the buttons on the screen
        #
        for button in self.test_buttons.values():
            button.redraw()
        return
    
    def rescanTestsCB(self):
        """Reload and rescan all modules looking for tests.
        """
        trace.into('ProctorGUI', 'rescanTestsCB')
        if self.state == 'idle':
            self.busyStart()
            self._buildScanner()
            self._updateTestButtons()
            self.busyEnd()
        else:
            self.showError('Cannot rescan during a test run.  Reset first.')
        trace.outof()
        return

    def changeScanDirectoryCB(self, *args):
        """Callback to bring up change directory dialog.
        """
        trace.into('ProctorGUI', 'changeScanDirectoryCB', args=args)
        if self.state == 'idle':
            file_name = tkFileDialog.askopenfilename(
                title='Select a file in the directory to scan...')
            trace.writeVar(file_name=file_name)
            directory_name = os.path.dirname(file_name)
            trace.writeVar(directory_name=directory_name)
            if directory_name:
                prefix = os.path.commonprefix((self.scan_directory_parent, directory_name))
                remainder = directory_name[len(prefix)+1:]
                self.scan_directory.set(remainder)
        else:
            self.showError('Cannot rescan during a test run.  Reset first.')
        trace.outof()
        return
    
    def _changeScanDirectoryVariableCB(self, *args):
        """Callback executed when variable containing scan directory changes.
        """
        trace.into('ProctorGUI', '_changeScanDirectoryCB', args=args)
        self._buildScanner()
        trace.outof()
        return
    
    def testButtonCB(self, testId):
        """Callback executed when user clicks on a callback.
        """
        button = self.test_buttons[testId]
        if self.result:
            self.showTestOutput(testId)
        return

    def resetTestsCB(self):
        """Reset the UI and clear all test results.
        """
        trace.into('ProctorGUI', 'resetTestsCB')
        self.tests = []
        self.result = None
        self.resetTestButtons()
        self.setState('idle')
        self.showTestOutput(None)
        self.updateProgress(0)
        trace.outof()
        return

    def showTestBalloonCB(self, testButton, msg):
        self.showMessage('help', msg)
        return

    ##
    ## SUPPORT FUNCTIONS
    ##

    def _createAllTestButtons(self, moduleTree=None):
        trace.into('ProctorGUI', '_createAllTestButtons')
        all_tests = moduleTree.getTestSuite(1)
        num_tests = all_tests.countTestCases()

        self.showMessage('userevent', '%d tests' % num_tests)

        trace.writeVar(num_tests=num_tests)

        #
        # Get preferences
        #
        width = self.user_preferences['width']
        height = self.user_preferences['height']
        spacing = self.user_preferences['spacing']
        
        #
        # Do some math to figure out how big to make the buttons.
        # Lean towards a more horizontal layout.
        #
        canvas_height = self.canvas.winfo_height()
        canvas_width = self.canvas.winfo_width()

        trace.writeVar(canvas_height=canvas_height,
                       canvas_width=canvas_width,
                       )
        
        num_per_row = ((canvas_width / (width + spacing))
                       or
                       1
                       )
        num_rows = (num_tests / num_per_row)
        if (num_tests % num_per_row):
            num_rows += 1

        #
        # Store values for use later
        #
        self._button_height = height
        self._button_width = width
        self._num_per_row = num_per_row
        self._row = 0
        self._col = 0

        #
        # Resize the canvas (height only)
        #
        required_height = num_rows * (self._button_height + spacing)
        trace.writeVar(required_height=required_height)
        if canvas_height > (required_height + self._button_height):
            trace.write('resizing down')
            do_resize = 1
        elif canvas_height < required_height:
            trace.write('resizing up')
            do_resize = 1
        else:
            do_resize = 0

        if do_resize:
            canvas = self.component('testcanvas')
            hull = canvas.component('hull')
            hull.configure(height=required_height)
        
        moduleTree.walk(self._makeTestButtons)

        trace.outof()
        return
    
    def _makeTestButtons(self, node, data=None):
        """Create a button for each test.

        This method is called as part of walking the module tree.
        """
        trace.into('ProctorGUI', '_makeTestButtons')
        #
        # Get the tests
        #
        test_suite = node.getTestSuite()
        tests = self._flattenTestSuite(test_suite)

        spacing = self.user_preferences['spacing']
        
        #
        # Create the buttons
        #
        for test in tests:
            trace.into('', 'tests', row=self._row, col=self._col)
            
            ulx = (self._button_width + spacing) * self._col
            uly = (self._button_height + spacing) * self._row
            trace.writeVar(ulx=ulx, uly=uly)
            
            command = lambda b, e, s=self, t=test.id(): s.testButtonCB(testId=t)
            
            new_button = TestIcon(canvas=self.canvas,
                                  name=test.id(),
                                  command=command,
                                  balloonHelp=test.id(),
                                  balloonFcn=self.showTestBalloonCB,
                                  width=self._button_width,
                                  height=self._button_height,
                                  ulx=ulx,
                                  uly=uly,
                                  )
            
            self.test_buttons[ test.id() ] = new_button

            #
            # Increment our position counter.
            #
            self._col += 1
            if self._col == self._num_per_row:
                self._col = 0
                self._row += 1

            trace.outof()

        trace.outof()
        return
    
    def _updateTestButtons(self):
        """Update the actual test buttons.

        Remove any existing buttons, and make new buttons to
        correspond to each test.
        """
        trace.into('ProctorGUI', '_updateTestButtons')
        #
        # Remove any existing buttons
        #
        for name, button in self.test_buttons.items():
            button.delete()
            del self.test_buttons[name]
        self.update_idletasks()
        #
        # Make the new buttons
        #
        if self.scanner:
            module_tree = self.scanner.getModuleTree()
            self.test_buttons = {}
            self._createAllTestButtons(module_tree)
        trace.outof()
        return
    
    def _buildScanner(self):
        trace.into('ProctorGUI', '_buildScanner')
        scan_directory = os.path.join(self.scan_directory_parent, self.scan_directory.get())
        trace.write('variable: %s' % scan_directory)
        self.scanner = ModuleScanner()
        self.showMessage('busy', 'Scanning...')
        self.busyStart()
        self.scanner.scan(scan_directory)
        self.busyEnd()
        self.showMessage('busy', '')
        trace.outof()
        return

    def _setTestButtonColor(self, testId, color):
        """Set the test button to the specified color.
        """
        trace.into('ProctorGUI', '_setTestButtonColor', testId=testId, color=color)
        button = self.test_buttons[testId]
        button.configure(bg=color)
        self.update_idletasks()
        trace.outof()
        return

    def resetTestButtons(self):
        """Clear button colors
        """
        trace.into('ProctorGUI', 'resetTestButtons')
        for button in self.test_buttons.values():
            #button.configure(bg=self.PENDING_COLOR)
            button.setState('pending')
        trace.outof()
        return

    def stopTestsCB(self):
        self.setState('paused')
        return
    
    def runTestsCB(self):
        """Execute all of the tests in our suite.
        """
        trace.into('ProctorGUI', 'runTestsCB')
        if self.tests and self.state == 'running':
            #
            # We are already running, do nothing.
            #
            pass
        
        elif self.tests:
            #
            # The user hit Go after hitting Stop,
            # so resume where we left off.
            #
            self.resumeTests()

        else:
            #
            # Starting from scratch.
            #
            self.runTests()
            
        trace.outof()
        return

    ##
    ## UI STATE MANAGEMENT
    ##

    def setState(self, newState):
        trace.into('ProctorGUI', 'setState', newState=newState)
        
        if newState == 'idle':
            self.updateProgress(0)
            self.showMessage('busy')
            self.busyEnd()
            enable_widgets = [ self.component('changescandirectorybtn'),
                               self.go_button,
                               self.rescan_button,
                               self.reset_button,
                               ]
            disable_widgets = [ self.stop_button ]
            
        elif newState == 'running':
            self.busyStart()
            enable_widgets = [ self.stop_button ]
            disable_widgets = [ self.component('changescandirectorybtn'),
                                self.go_button,
                                self.rescan_button,
                                self.reset_button,
                                ]
            
        elif newState == 'paused':
            self.busyEnd()
            enable_widgets = [ self.go_button,
                               self.reset_button,
                               ]
            disable_widgets = [ self.component('changescandirectorybtn'),
                                self.rescan_button,
                                self.stop_button,
                                ]

        for w in disable_widgets:
            w.configure(state='disabled')

        for w in enable_widgets:
            w.configure(state='normal')
            
        self.state = newState
        trace.outof()
        return

    def runTests(self):
        #
        # Make sure we have a scanner.
        #
        if not self.scanner:
            self._buildScanner()
        else:
            self.scanner.getModuleTree().reload()
        #
        # Re-initialize UI
        #
        self._updateTestButtons()
        self.showTestOutput(None)
        #
        # Get a runner and the test suite
        #
        #runner = TestRunner(self)
        test_suite = self.scanner.getModuleTree().getTestSuite(1)
        #
        # Set up the progress meter
        #
        self.current_test_num = 0
        self.updateProgress(0, test_suite.countTestCases())
        #
        # Set the result set, and enable test running for the work proc
        #
        self.result = ProctorTestResult(app=self)
        self.tests = self._flattenTestSuite(test_suite)
        self.tests.reverse()
        self.setState('running')
        self.after(100, self.runOneTest)
        return

    def resumeTests(self):
        """Resume the existing test set.
        """
        self.setState('running')
        self.after(100, self.runOneTest)
        return

    def stopTests(self):
        self.setState('paused')
        return

    ##
    ## IDLE PROCESSING
    ##

    def runOneTest(self):
        if self.state == 'running' and self.tests:
            #
            # Run a test and re-register ourself.
            #
            test = self.tests.pop()
            test(self.result)
            self.after(100, self.runOneTest)
            
        elif self.tests:
            #
            # User hit stop, so do not process any tests or
            # re-register the after() handler.
            #
            pass
            
        else:
            #
            # We are back to the 'idle' state.
            #
            self.setState('idle')
            
        return

    ##
    ## TEST RESULT CALLBACKS
    ##
    
    def showTestOutput(self, testId):
        """Show the output from the specified test.
        """
        if testId:
            label_text = testId
            result_text, result_errors = self.result.getOutput(testId)
            display_text = '%s\n%s\n%s' % (result_errors, '-' * 80, result_text)
        else:
            label_text = ''
            display_text = ''
        self.output_text.configure(label_text=label_text)
        self.output_text.settext(display_text)
        return

    def showTestBegin(self, test):
        """Update the UI to reflect beginning of a test.
        """
        self.test_buttons[test.id()].setState('running')
        self.showMessage('busy', test.id())
        self.update_idletasks()
        return

    def showTestEnd(self, test):
        """Update the UI to reflect the end of a test.
        """
        self.current_test_num += 1
        self.updateProgress(self.current_test_num)
        self.update_idletasks()
        return

    def showTestError(self, test):
        """Update the UI to reflect the error from a test.
        """
        #self._setTestButtonColor(test.id(), self.ERROR_COLOR)
        self.test_buttons[test.id()].setState('error')
        self.update_idletasks()
        return

    def showTestFailure(self, test):
        """Update the UI to reflect a failure of a test.
        """
        #self._setTestButtonColor(test.id(), self.FAILURE_COLOR)
        self.test_buttons[test.id()].setState('failure')
        self.update_idletasks()
        return

    def showTestSuccess(self, test):
        """Update the UI to reflect the success of a test.
        """
        #self._setTestButtonColor(test.id(), self.SUCCESS_COLOR)
        self.test_buttons[test.id()].setState('success')
        self.update_idletasks()
        return

    def _flattenTestSuite(self, testSuite):
        """Convert a suite tree to a list of test cases.
        """
        l = []
        try:
            for test_suite in testSuite._tests:
                l = l + self._flattenTestSuite(test_suite)
        except AttributeError:
            l.append(testSuite)
        return l
    
