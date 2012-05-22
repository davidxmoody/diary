#!/usr/bin/env python3
# Script to launch the default editor on a specified diary entry.

import os
import sys
from subprocess import call
import diary_range

def edit_entry(filename, editor=os.environ['diary_edit_default_editor']):
    '''Execute editor on filename.
    
    Also creates the required directory structure if it does not exist.'''

    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    call('{} "{}"'.format(editor, filename), shell=True)


if len(sys.argv) <= 1:
    # Edit last entry.
    edit_entry(*diary_range.single_entry(-1))
else:
    # Edit all entries specified with args.
    diary_range.process_args(edit_entry)
