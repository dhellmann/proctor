#!/usr/bin/env python
#
# $Id$
#
# Time-stamp: <03/04/23 08:14:26 dhellmann>
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
"""Distutils setup file for Proctor

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile$',
    'rcs_id'       : '$Id$',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'Proctor',
    'created'      : 'Sat, 03-Feb-2001 12:51:26 EST',

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
from distutils.core import setup
import string
import sys

#
# Import Local modules
#

#
# Module
#

BSD_LICENSE="""

                    Copyright 2001, 2002 Doug Hellmann.

                         All Rights Reserved

Permission to use, copy, modify, and distribute this software and
its documentation for any purpose and without fee is hereby
granted, provided that the above copyright notice appear in all
copies and that both that copyright notice and this permission
notice appear in supporting documentation, and that the name of Doug
Hellmann not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior
permission.

DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

LONG_DESCRIPTION = """
    Proctor is a tool for running unit tests.  It enhances the
    standard unittest module to provide the ability to find all tests
    in a set of code, categorize them, and run some or all of them.
    Test output may be generated in a variety of formats to support
    parsing by another tool or simple, nicely formatted, reports for
    human review.
"""


def cvsProductVersion(cvsVersionString='$Name$'):
    """Function to return the version number of the program.

    The value is taken from the CVS tag, assuming the tag has the form:

        rX_Y_Z

    Where X is the major version number, Y is the minor version
    number, and Z is the optional sub-minor version number.
    """
    cvs_version_parts=string.split(cvsVersionString)
    if len(cvs_version_parts) >= 3:
        app_version = string.strip(cvs_version_parts[1]).replace('_', '.')
        if app_version and app_version[0] == 'r':
            app_version = app_version[1:]
    else:
        app_version = 'WORKING'
    return app_version



setup (
    name = 'Proctor',
    version = cvsProductVersion(),

    description = 'Proctor Test Runner',
    long_description = LONG_DESCRIPTION,

    author = 'Doug Hellmann',
    author_email = 'doug@hellfly.net',

    url = 'http://sourceforge.net/projects/proctor',
    license = BSD_LICENSE,

    platforms = ('Any',),
    keywords = ('test', 'testing', 'unittest'),

    packages = [ 'proctorlib',
                 ],
    
    package_dir = { '': '.' },
    
    scripts = ['proctorbatch'],

#     discriminators = [ 'Operating System :: OS Independent',
#                        'Environment :: Console (Text Based)',
#                        'Programming Language :: Python',
#                        'License :: OSI Approved :: BSD License',
#                        'Development Status :: 5 - Production/Stable',
#                        'Intended Audience :: Developers',
#                        'Topic :: Software Development',
#                        ],
    )

