from config import pad_char, color_middle, color_padding, color_end, terminal_width
import textwrap
import time

def get_date_string(entry, format='%A %d %B %Y %I:%M%p'):
    '''Return formatted string representing the entry creation date.'''
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

def formatted(entry, width=terminal_width):
    '''Return a list of formatted lines, wrapped to width.'''
    return '\n'.join(_gen_formatted(entry, width)) + '\n\n'
