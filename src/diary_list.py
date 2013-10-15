#!/usr/bin/env python3

import diary_range
from diary_tui import formatted
import sys
from subprocess import Popen, PIPE

def display_entries(entries):
    '''Open a less pipe to display the given entries to the user.'''

    less_process = Popen('less -R', stdin=PIPE, shell=True)

    for entry in entries:
        if less_process.poll() is None:  # Still running
            less_process.stdin.write(bytes(formatted(entry), 'UTF-8'))

    less_process.stdin.close()
    less_process.wait()
    

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        # TODO change default range to something better or use lazy evaluation
        display_entries(diary_range.last(100))
    else:
        display_entries(diary_range.process_args())
