#!/usr/bin/env python3
# Script to launch the default editor on a specified diary entry.

import os
import sys
from subprocess import call
import diary_range

def edit_entry(entry, 
               editor_existing=os.environ['diary_edit_default_editor'],
               editor_new=os.environ['diary_new_entry_default_editor']):
    '''Execute editor on filename.
    
    Also creates the required directory structure if it does not exist.'''

    entry.mkdir()

    editor = editor_existing if entry.exists() else editor_new

    call('{} "{}"'.format(editor, entry.pathname), shell=True)


if len(sys.argv) <= 1:
    # Edit last entry.
    edit_entry(*diary_range.single_entry(-1))
else:
    # Edit all entries specified with args.
    # TODO add delay/the ability to cancel editing multiple entries.
    for entry in diary_range.process_args():
        edit_entry(entry)
