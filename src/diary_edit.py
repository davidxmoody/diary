#!/usr/bin/env python3
# Script to launch the default editor on a specified diary entry.

import sys
from subprocess import call
import diary_range
import config

def edit_entry(entry, 
               editor_existing=config.default_editor_existing,
               editor_new=config.default_editor_new):
    '''Execute editor on filename.
    
    Also creates the required directory structure if it does not exist.'''

    entry.mkdir()

    editor = editor_existing if entry.exists() else editor_new

    call('{} "{}"'.format(editor, entry.pathname), shell=True)




if len(sys.argv) <= 1:
    entry = diary_range.single_entry(-1).__next__()
else:
    entry = diary_range.process_args().__next__()

edit_entry(entry)
