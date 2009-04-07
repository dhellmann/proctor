#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2009 Doug Hellmann All rights reserved.
#
"""
"""

# Standard library
import copy
import os

# Third-party

# Set up Paver
import paver
import paver.misctasks
from paver.path import path
from paver.easy import *
import paver.setuputils
paver.setuputils.install_distutils_tasks()

# What project are we building?
PROJECT = 'Proctor'
VERSION = '1.5'

# Read the long description to give to setup
README_FILE = 'README.txt'
README = path(README_FILE).text()

# Scan the input for package information
# to grab any data files (text, images, etc.) 
# associated with sub-packages.
PACKAGE_DATA = paver.setuputils.find_package_data('proctorlib', 
                                                  package='proctorlib',
                                                  only_in_packages=True,
                                                  )

options(
    setup=Bunch(
        name = PROJECT,
        version = VERSION,
        
        description = 'Proctor Test Runner',
        long_description = README,

        author = 'Doug Hellmann',
        author_email = 'doug.hellmann@gmail.com',

        url = 'http://www.doughellmann.com/projects/%s/' % PROJECT,
        download_url = 'http://www.doughellmann.com/downloads/%s-%s.tar.gz' % \
                        (PROJECT, VERSION),

        classifiers = [ 'Development Status :: 5 - Production/Stable',
                        'License :: OSI Approved :: BSD License',
                        'Programming Language :: Python',
                        'Intended Audience :: Developers',
                        'Environment :: Console',
                        ],

        platforms = ('Any',),
        keywords = ('test', 'testing', 'unittest'),

        # packages = [ 'proctorlib',
        #              ],
        # 
        # package_dir = { '': '.' },

        scripts = ['proctorbatch', 
                   'proctorfilter', 
                   'coveragemerge',
                   ],

        provides=['Proctor',
                  'proctorlib',
                  ],
        requires=['coverage (>=2.77)'],

        data_files=[('docs', ['README.html']),
                    ],

        # It seems wrong to have to list recursive packages explicitly.
        packages = sorted(PACKAGE_DATA.keys()),
        package_data=PACKAGE_DATA,

        zip_safe=False,

        ),
    
    sdist = Bunch(
        dist_dir=os.path.expanduser('~/Desktop'),
    ),
    
)

@task
@needs(['html', 'generate_setup', 'minilib', 
        'setuptools.command.sdist'
        ])
def sdist():
    """Create a source distribution.
    """
    pass

@task
def html():
    # FIXME - Switch to sphinx?
    outfile = path('README.html')
    outfile.unlink()
    sh('rst2html.py %s README.html' % README_FILE)
    return

@task
def test():
    sh('proctorbatch proctorlib')
    return
