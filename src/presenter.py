from subprocess import check_output, Popen, PIPE
import textwrap
import time

PAD_CHAR = '='
COLOR_MIDDLE = '\033[1;34m'   # Bold blue.
COLOR_PADDING = '\033[0;34m'  # Blue.
COLOR_END = '\033[0m'

DATE_FORMAT = '%a %d %b %Y %H:%M'
TERMINAL_WIDTH = int(check_output('tput cols', shell=True).strip())


def get_date_string(entry, format=DATE_FORMAT):
    '''Return formatted string representing the entry creation date.'''
    return time.strftime(format, time.localtime(float(entry.timestamp)))

def get_header(entry, width):
    '''Return a colored header string padded to the correct width.'''

    left = PAD_CHAR + '{} words'.format(entry.wordcount())
    right = str(entry.timestamp) + PAD_CHAR
    middle = ' {} '.format(get_date_string(entry))

    padding_left = PAD_CHAR * int(width/2 - len(left) - len(middle)/2)
    padding_right = PAD_CHAR * (width - len(left) - 
                        len(padding_left) - len(middle) - len(right))

    return COLOR_PADDING +     left      + padding_left + COLOR_END + \
           COLOR_MIDDLE  +            middle            + COLOR_END + \
           COLOR_PADDING + padding_right +    right     + COLOR_END

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

def formatted(entry, width=TERMINAL_WIDTH):
    '''Return a list of formatted lines, wrapped to width.'''
    return '\n'.join(_gen_formatted(entry, width)) + '\n\n'

def display_entries(entries):
    '''Open a less pipe to display the given entries to the user.'''

    less_process = Popen('less -R', stdin=PIPE, shell=True)

    try:
        for entry in entries:
            less_process.stdin.write(bytes(formatted(entry), 'UTF-8'))
        less_process.stdin.close()
        less_process.wait()

    except BrokenPipeError:
        # Less process closed by user (hopefully) so stop quietly
        pass
