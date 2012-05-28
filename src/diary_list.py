#!/usr/bin/env python3

import diary_range
import sys
from subprocess import Popen, PIPE

less_process = None

def display_entry(entry):
    global less_process

    if not entry.exists(): 
        return

    if less_process is None:
        less_process = Popen('less -R', stdin=PIPE, shell=True)

    if less_process.poll() is None:  # Still running
        less_process.stdin.write(bytes(entry.formatted(), 'UTF-8'))


if len(sys.argv) <= 1:
    # TODO change default range to something better or use lazy evaluation
    entries = diary_range.last(600)
else:
    entries = diary_range.process_args()

for entry in entries:
    display_entry(entry)

less_process.stdin.close()
less_process.wait()
