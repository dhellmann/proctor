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

"""Scan directory for files.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile$',
    'rcs_id'       : '$Id$',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'Proctor',
    'created'      : 'Sat, 15-Jun-2002 11:35:07 EDT',

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
import imp
import sys
import unittest
from UserDict import UserDict

#
# Import Local modules
#
import os
from proctorlib.trace import trace

#
# Module
#

_module_cache = {}

class ModuleTree:

    TRACE_LEVEL=3
    
    def __init__(self, name='', parent=None):
        trace.into('ModuleTree', '__init__', name=name, parent=parent,
                   outputLevel=self.TRACE_LEVEL)
        self.name = name
        self.parent = parent
        self.data = {}

        self.reload()
        
        trace.outof(outputLevel=self.TRACE_LEVEL)
        return

    def _importModule(self):
        trace.into('ModuleTree', '_importModule', outputLevel=self.TRACE_LEVEL)
        if self.name:
            try:
                full_name = self.getName()

                path_name = full_name.replace('.', '/')
                directory, module_base = os.path.split(path_name)
                
                trace.write('find_module(%s, [%s])' % (module_base, directory),
                            outputLevel=self.TRACE_LEVEL)

                module = None
                global _module_cache
                try:
                    module = _module_cache[(module_base, directory)]
                    trace.write('Found module %s.%s in cache' % (directory,
                                                                 module_base,
                                                                 )
                                )
                except KeyError:
                    fp, pathname, description = imp.find_module(module_base,
                                                                [directory])

                    trace.writeVar(module_base=module_base,
                                   fp=fp,
                                   pathname=pathname,
                                   description=description,
                                   outputLevel=self.TRACE_LEVEL)



                    try:
                        load_module_args = (module_base, fp, pathname, description)
                        trace.write('load_module%s' % str(load_module_args), outputLevel=self.TRACE_LEVEL)
                        try:
                            module = apply(imp.load_module, load_module_args)
                        except Exception, msg:
                            raise ImportError(str(msg))

                        _module_cache[(module_base, directory)] = module
                    finally:
                        if fp:
                            fp.close()
                
            except ImportError, msg:
                #
                # Could not import the thing, so assume that it is
                # either a bad module (syntax error, etc.), or
                # not a python file anyway.
                #
                sys.stderr.write('WARNING: Could not import %s (%s)\n' % (full_name, msg))
                module = None
        else:
            #
            # No name, so no module at this point in the tree
            #
            module = None

        self.module = module
        #if self.parent and self.parent.module:
        #    trace.write('Setting %s attribute of %s to %s' % (self.name, self.parent.module, module),
        #                outputLevel=self.TRACE_LEVEL)
        #    setattr(self.parent.module, self.name, module)
        trace.outof(outputLevel=self.TRACE_LEVEL)
        return module

    def getFullModule(self):
        if self.parent:
            parent_module = self.parent.getFullModule()
            if parent_module:
                print 'Getting %s from %s' % (self.name, parent_module)
                sys.stdout.flush()
                module = getattr(parent_module, self.name)
            else:
                module = self.module
        else:
            module = self.module
        return module

    def reload(self):
##        if hasattr(self, 'module') and self.module:
##            #reload(self.getFullModule())
##            reload(self.module)
##        else:
        self._importModule()
        self._loadTests()
        for child in self.data.values():
            child.reload()
        return

    def _ignoreModule(self, module):
        trace.into('ModuleTree', '_ignoreModule', outputLevel=self.TRACE_LEVEL)

        if not module:
            return trace.outof(1, outputLevel=self.TRACE_LEVEL)
        
        if hasattr(module, '__proctor_ignore_module__') and module.__proctor_ignore_module__:
            return trace.outof(1, outputLevel=self.TRACE_LEVEL)

        return trace.outof(0, outputLevel=self.TRACE_LEVEL)

    def _addTestsToSuite(self, tests=()):
        """Callback called by the TestLoader as it finds sets of tests.
        """
        if not tests:
            return

        trace.write('Got %d tests' % len(tests),
                    outputLevel=self.TRACE_LEVEL)
        
        for test in tests:
            #
            # Why are there null tests?
            #
            if not test:
                continue
            
            try:
                categories = test.PROCTOR_TEST_CATEGORIES
            except AttributeError:
                self._getTestSuite('Unspecified').addTest(test)
            else:
                for category in categories:
                    test_suite = self._getTestSuite(category)
                    test_suite.addTest(test)

            self._getTestSuite('All').addTest(test)
        #
        # Return a bogus suite so the TestLoader works
        # right.  This is all thrown away when the scan
        # is completed.
        #
        return unittest.TestSuite()

    def _loadTests(self):
        trace.into('ModuleTree', '_loadTests', outputLevel=self.TRACE_LEVEL)
        self.test_suites = {}
        if self._ignoreModule(self.module):
            trace.write('No module', outputLevel=self.TRACE_LEVEL)
            self.test_loader = None
        else:
            trace.write('Loading tests', outputLevel=self.TRACE_LEVEL)
            self.test_loader = unittest.TestLoader()
            self.test_loader.suiteClass = self._addTestsToSuite
            self.test_loader.loadTestsFromModule(self.module)
            #trace.writeVar(self_test_suite=self.test_suite,
            #               outputLevel=self.TRACE_LEVEL)
        trace.outof(outputLevel=self.TRACE_LEVEL)
        return

    def _getTestSuite(self, category):
        """Returns the internal test suite (no children) for the given category.
        """
        test_suite = self.test_suites.get(category)
        if not test_suite:
            test_suite = unittest.TestSuite()
            self.test_suites[category] = test_suite
        return test_suite

    def getTestCategories(self, categoryList=None):
        if categoryList is None:
            categoryList = []
        #
        # Categories at this level
        #
        my_categories = self.test_suites.keys()
        for my_category in my_categories:
            if my_category not in categoryList:
                categoryList.append(my_category)

        #
        # Recurse
        #
        children = self.data.items()
        for child_name, child_node in children:
            child_node.getTestCategories(categoryList)

        return categoryList

    def getTestSuite(self, full=0, category='All'):
        trace.into('ModuleTree', 'getTestSuite', outputLevel=self.TRACE_LEVEL)
        test_suite = unittest.TestSuite()
        #
        # Add our own suite of local tests
        #
        category_test_suite = self._getTestSuite(category)
        if category_test_suite.countTestCases():
            test_suite.addTest(category_test_suite)
        #
        # Get suites from our children
        #
        if full:
            children = self.data.items()
            #children.sort()
            for child_name, child_node in children:
                child_tests = child_node.getTestSuite(full=full, category=category)
                if child_tests.countTestCases():
                    test_suite.addTest(child_tests)
        return trace.outof(test_suite, outputLevel=self.TRACE_LEVEL)

    def walk(self, callable, data=None):
        callable(self, data)
        for child_node in self.data.values():
            child_node.walk(callable, data=data)
        return
    
    def getName(self):
        """Returns the full module name pointing to the module.
        """
        if self.parent and self.parent.getName():
            prefix = '%s.' % self.parent.getName()
        else:
            prefix = ''
        return prefix + self.name

    def _getKeyParts(self, key):
        trace.into('ModuleTree', '_getKeyParts', key=key, outputLevel=self.TRACE_LEVEL)
        key_parts = key.split('.')
        trace.outof(key_parts, outputLevel=self.TRACE_LEVEL)
        return key_parts

    def __getitem__(self, key):
        """The key might be a full or partial module path.  In all cases,
        it is assumed to be relative from the current point in the
        module tree.
        """
        trace.into('ModuleTree', '__getitem__', key=key,
                   outputLevel=self.TRACE_LEVEL)
        key_parts = self._getKeyParts(key)
        try:
            #
            # The first part of the key should be our child.
            #
            child_node = self.data[key_parts[0]]
            #
            # If there is a remaining part of the key, it is
            # the name of a node under the child node.
            #
            if len(key_parts) > 1:
                item = child_node[ '.'.join(key_parts[1:]) ]
            else:
                item = child_node
        except KeyError:
            trace.outof('not found', outputLevel=self.TRACE_LEVEL)
            raise
        else:
            trace.outof(item, outputLevel=self.TRACE_LEVEL)
        return item

    def newNode(self, name):
        node = self.__class__(name=name, parent=self)
        return node

    def __setitem__(self, key, value):
        trace.into('ModuleTree', '__setitem__', key=key, value=value,
                   outputLevel=self.TRACE_LEVEL)
        key_parts = self._getKeyParts(key)
        trace.writeVar(key_parts=key_parts, outputLevel=self.TRACE_LEVEL)
        #
        # Separate the part of the key that is the name of the
        # value from the path to the key.
        #
        value_name = key_parts[-1]
        key_parts = key_parts[:-1]
        trace.writeVar(value_name=value_name, key_parts=key_parts,
                       outputLevel=self.TRACE_LEVEL)
        #
        # Create intermediate nodes, if necessary.
        #
        child_node = self
        for node_name in key_parts:
            trace.write('handling node name %s' % node_name,
                        outputLevel=self.TRACE_LEVEL)
            try:
                trace.write('looking for %s' % node_name,
                            outputLevel=self.TRACE_LEVEL)
                child_node = child_node[node_name]
                trace.write('got %s' % node_name, outputLevel=self.TRACE_LEVEL)
            except KeyError:
                trace.write('creating child node', outputLevel=self.TRACE_LEVEL)
                new_child_node = child_node.newNode(name=node_name)
                child_node.data[node_name] = new_child_node
                child_node = new_child_node
                trace.write('created %s' % node_name, outputLevel=self.TRACE_LEVEL)
        child_node.data[value_name] = child_node.newNode(value_name)
        trace.outof(outputLevel=self.TRACE_LEVEL)
        return
        
    

class ModuleScanner:
    """Scanner to find modules in a directory tree.

    TO DO

     1. Need to make the scanner capable of looking at a directory
     other than.  Probably need to strip a prefix from the value sent
     to the ModuleTree.
     
    """

    TRACE_LEVEL=2

    SKIP_NAMES = ('CVS', 'setup.py', '__init__.py')
    SKIP_FILE_EXTENSIONS = ('pyc', 'pyo', 'pyd', 'html', 'txt', 'py~')

    def __init__(self, verboseLevel=0):
        trace.into('ModuleScanner', '__init__', outputLevel=self.TRACE_LEVEL)
        self.verbose_level = verboseLevel
        self.module_tree = ModuleTree()
        trace.outof(outputLevel=self.TRACE_LEVEL)
        return
    
    def getTestSuite(self, category=None):
        return self.module_tree.getTestSuite(full=1, category=category)

    def getModuleTree(self):
        return self.module_tree

    def scan(self, directoryName):
        trace.into('ModuleScanner', 'scan', directoryName=directoryName,
                   outputLevel=self.TRACE_LEVEL)
        if os.path.isdir(directoryName):
            os.path.walk(directoryName, self.walkCallback, None)
        else:
            self.walkCallback(None,
                              os.path.dirname(directoryName),
                              [ os.path.basename(directoryName) ])
        trace.outof(outputLevel=self.TRACE_LEVEL)
        return

    def walkCallback(self, arg, dirname, filenames):
        trace.into('ModuleScanner', 'walkCallback',
                   arg=arg, dirname=dirname, filenames=filenames,
                   outputLevel=self.TRACE_LEVEL)
        if self.verbose_level:
            print 'Scanning: %s' % dirname
            sys.stdout.flush()
        #
        # Create a local copy of the names to skip, then add
        # .cvsignore content to it if the file exists.
        #
        skip_names = list(self.SKIP_NAMES[:])
        if '.cvsignore' in filenames:
            try:
                ignore_file = open(os.path.join(dirname, '.cvsignore'), 'r')
            except IOError:
                trace.write('Unable to open .cvsignore file in %s' % dirname)
            else:
                ignore_files = ignore_file.readlines()
                ignore_file.close()
                ignore_files = [ f.strip() for f in ignore_files ]
                skip_names = skip_names + ignore_files
                
        #
        # Update the local copy of the names to skip
        # with .proctor configuration if the file exists.
        #
        if '.proctor' in filenames:
            try:
                proctor_file = open(os.path.join(dirname, '.proctor'), 'r')
            except IOError:
                trace.write('Unable to open .proctor file in %s' % dirname)
            else:
                proctor_file_body = proctor_file.read()
                proctor_file.close()
                global_namespace = {}
                local_namespace = {}
                try:
                    exec proctor_file_body in global_namespace, local_namespace
                except:
                    import traceback
                    sys.stderr.write('\n--- Config File Error %s/.proctor ---\n' % dirname)
                    traceback.print_exc()
                    sys.stderr.write('--------------------------------------------\n\n')
                else:
                    skip_names = skip_names + list(local_namespace['ignore'])
                
        #
        # First, skip over directories we are not interested in
        # scanning.
        #
        for skip_name in skip_names:
            if skip_name in filenames:
                trace.write('Skipping %s' % skip_name, outputLevel=self.TRACE_LEVEL)
                del filenames[filenames.index(skip_name)]
        #
        # Clean up the directory name
        #
        normalized_dirname = os.path.normpath(dirname)
        trace.write('normalized path=%s' % normalized_dirname,
                    outputLevel=self.TRACE_LEVEL)
        #
        # Get the relative path
        #
        common_prefix = os.path.commonprefix( (os.getcwd(), normalized_dirname) )
        if common_prefix:
            prefix_len = len(common_prefix) + len(os.sep)
            normalized_dirname = normalized_dirname[prefix_len:]
        #
        # Convert the directory name to a module path
        #
        dirname_parts = normalized_dirname.split(os.sep)
        package_path = '.'.join(dirname_parts)
        trace.writeVar(package_path=package_path, outputLevel=self.TRACE_LEVEL)
        for filename in filenames:
            #
            # Skip files with bad extensions or prefixes.
            #
            base_filename, extension = os.path.splitext(filename)
            extension = extension[1:]
            
            if extension in self.SKIP_FILE_EXTENSIONS:
                trace.write('Skipping file %s/%s' % (normalized_dirname, filename),
                            outputLevel=self.TRACE_LEVEL)
                
            elif filename[0] == '.':
                trace.write('Skipping file %s/%s' % (normalized_dirname, filename),
                            outputLevel=self.TRACE_LEVEL)
                
            elif extension == 'py':
                #
                # If we are looking in ., put the new module
                # at the root of the module tree.  Otherwise,
                # build the import path to the module as the
                # key.
                #
                if package_path == os.curdir:
                    module_path = base_filename
                else:
                    module_path = '%s.%s' % (package_path, base_filename)
                trace.write('Adding %s' % module_path, outputLevel=self.TRACE_LEVEL)
                self.module_tree[module_path] = module_path
                
            else:
                trace.write('Skipping file %s/%s' % (normalized_dirname, filename),
                            outputLevel=self.TRACE_LEVEL)
                
        trace.outof(outputLevel=self.TRACE_LEVEL)
        return
    
