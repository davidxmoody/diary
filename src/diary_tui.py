#!/usr/bin/env python3

# This script should:
# - Provide all functionality currently provided by the `diary` script. 
# - Encapsulate everything related to using the diary scripts from a terminal.

from diary_range import cached
import config
from config import pad_char, color_middle, color_padding, color_end
import textwrap
import time

def get_date_string(entry, format='%A %d %B %Y %I:%M%p'):
    '''Return formatted string representing the entry creation date.'''
    # TODO add additional information (like today/yesterday/in the future).
    return time.strftime(format, time.localtime(float(entry.timestamp)))

def get_header(entry, width):
    '''Return a colored header string padded to the correct width.'''

    left = pad_char + '{} words'.format(entry.wordcount())
    right = str(entry.timestamp) + pad_char
    middle = ' {} '.format(get_date_string(entry))

    padding_left = pad_char * int(width/2 - len(left) - len(middle)/2)
    padding_right = pad_char * (width - len(left) - 
                        len(padding_left) - len(middle) - len(right))

    return color_padding +     left      + padding_left + color_end + \
           color_middle  +            middle            + color_end + \
           color_padding + padding_right +    right     + color_end

# TODO add search term highlighting after this stage
# TODO skip final lines if they are empty?
# TODO add markdown formatting?
# TODO put header generation in separate method?
def _gen_formatted(entry, width):
    '''Return a generator over the formatted, wrapped lines of an entry.'''

    yield get_header(entry, width)

    wrapper = textwrap.TextWrapper(width=width)

    for line in entry._gen_text():
        wrapped_text = wrapper.wrap(line)
        if len(wrapped_text) == 0:
            yield ''
        for wrapped_line in wrapped_text:
            yield wrapped_line

# It's kind of a cheat to use cached on a non-method.
@cached
def _formatted(entry, width):
    return '\n'.join(_gen_formatted(entry, width)) + '\n\n'
            
def formatted(entry, width=config.terminal_width):
    '''Return a list of formatted lines, wrapped to width.'''
    return _formatted(entry, width)
