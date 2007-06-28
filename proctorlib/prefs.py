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

"""Preferences for the GUI.

"""

__module_id__ = '$Id$'

#
# Import system modules
#


#
# Import Local modules
#
import PmwContribD

#
# Module
#

class ProctorPrefs(PmwContribD.UserPrefs):

    order = (
        'spacing',
        'width',
        'height',
        'background',
        'pending',
        'running',
        'success',
        'failure',
        'error',
        )
    allowedValues = {
        'spacing'    : ('integer', 5, 'Space between test indicators'),
        'width'      : ('integer', 20, 'Width of test indicators'),
        'height'     : ('integer', 20, 'Height of test indicators'),
        'background' : ('color', 'black', 'Background color'),
        'pending'    : ('color', 'grey',  'Test pending color'),
        'running'    : ('color', 'cyan',  'Test running color'),
        'success'    : ('color', 'green', 'Success indicator color'),
        'failure'    : ('color', 'red', 'Failure indicator color'),
        'error'      : ('color', 'yellow', 'Error indicator color'),
        }
