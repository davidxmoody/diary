from subprocess import check_output, Popen, PIPE
import textwrap
import time

pad_char = '='
color_middle = '\033[1;34m'   # Bold blue.
color_padding = '\033[0;34m'  # Blue.
color_bold = '\033[1;37m'     # Bold white.
color_end = '\033[0m'

terminal_width = int(check_output('tput cols', shell=True).strip())


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

def display_entries(entries):
    '''Open a less pipe to display the given entries to the user.'''

    less_process = Popen('less -R', stdin=PIPE, shell=True)

    for entry in entries:
        if less_process.poll() is None:  # Still running
            less_process.stdin.write(bytes(formatted(entry), 'UTF-8'))

    less_process.stdin.close()
    less_process.wait()
