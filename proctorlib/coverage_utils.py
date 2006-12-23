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

"""Merge coverage files from multiple sources into a single file.

"""

__rcs_info__ = {
    #
    #  Creation Information
    #
    'module_name'  : '$RCSfile$',
    'rcs_id'       : '$Id$',
    'creator'      : 'Doug Hellmann <doug@hellfly.net>',
    'project'      : 'Proctor',
    'created'      : 'Wed, 23-Oct-2002 14:50:10 EDT',

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
import marshal


#
# Import Local modules
#


#
# Module
#

def detailed_getMergedData(coverageFilenames):

    all_data = {}
    
    for filename in coverageFilenames:
        #print 'Unmarshalling %s' % filename

        #
        # Retrieve the data from each file
        #
        f = open(filename, 'rb')
        try:
            new_data = marshal.load(f)
        finally:
            f.close()

        #
        # Merge the data into the
        # combined data set.
        #
        for module_filename, module_data in new_data.items():
            existing_data = all_data.setdefault(module_filename, {})

            #print 'Working on %s' % module_filename
            
            for line_num, count in module_data.items():
                current = existing_data.get(line_num, 0)
                new_val = existing_data.get(line_num, 0) + count
                #print 'Updating %s from %s to %s' % (line_num, current, new_val)
                existing_data[line_num] = new_val

    return all_data

def getMergedData(coverageFilenames):

    all_data = {}
    
    for filename in coverageFilenames:
        #print 'Unmarshalling %s' % filename

        #
        # Retrieve the data from each file
        #
        f = open(filename, 'rb')
        try:
            new_data = marshal.load(f)
        finally:
            f.close()

        #
        # Merge the data into the
        # combined data set.
        #
        for module_filename, module_data in new_data.items():
            existing_data = all_data.setdefault(module_filename, {})

            existing_data.update(module_data)

    return all_data

def saveMergedData(outputFileName, mergedData):
    output = open(outputFileName, 'wb')
    try:
        #print 'Writing %s' % outputFileName
        marshal.dump(mergedData, output)
    finally:
        output.close()
    return

if __name__ == '__main__':
    import sys

    output_file = sys.argv[1]
    input_files = sys.argv[2:]
    
    data = getMergedData(input_files)

    saveMergedData(output_file, data)
