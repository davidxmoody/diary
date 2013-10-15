#!/usr/bin/env python3
# Script to launch the default editor on a specified diary entry.

import sys
from subprocess import call
import diary_range

DEFAULT_EDITOR_EXISTING = 'vim "+syntax off" "+set spell" "+set nonumber" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
DEFAULT_EDITOR_NEW = DEFAULT_EDITOR_EXISTING + ' "+startinsert"'

def edit_entry(entry, 
               editor_existing=DEFAULT_EDITOR_EXISTING,
               editor_new=DEFAULT_EDITOR_NEW):
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
