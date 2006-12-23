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

"""Test Icon

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile$',
    'rcs_id'       : '$Id$',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'UNSPECIFIED',
    'created'      : 'Wed, 19-Jun-2002 10:50:25 EDT',

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
import Canvas
import PmwContribD


#
# Import Local modules
#
from trace import trace

#
# Module
#

class TestIcon(PmwContribD.AnimatedIcon.AnimatedIcon):
    """Icon representing a Test.
    """

    COLORS = {
        'pending' : 'grey',
        'running' : 'cyan',
        'success' : '#009c00',
        'error'   : 'yellow',
        'failure' : 'red',
        }

    state = 'pending'

    def createImage(self):
        trace.into('TestIcon', 'createImage')
        trace.writeVar(name=self.name)
        self.box = Canvas.Rectangle(self.canvas,
                                    (self.ulx, self.uly,
                                     self.ulx + self.width, self.uly + self.height,
                                     ),
                                    fill=self.COLORS['pending'],
                                    outline=self.COLORS['pending'],
                                    )
        self.box.addtag(self.uniqueName)
        self.canvas_objects.append(self.box)
        trace.write('balloonFcn=%s' % self.balloonFcn)
        trace.outof()
        return

    def setState(self, newState):
        trace.into('TestIcon', 'setState', newState=newState)
        trace.write('%s: %s, %s' % (self.name, self.ulx, self.uly))
        self.state = newState
        color = self.COLORS[self.state]
        trace.writeVar(color=color)
        self.box.config(fill=color, outline=color)
        self.canvas.update_idletasks()
        trace.outof()
        return

    def getState(self):
        return self.state

    def redraw(self):
        self.setState(self.state)
        return
    
