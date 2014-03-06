from subprocess import check_output, Popen, PIPE
from textwrap import TextWrapper
import re
from shutil import get_terminal_size

TERMINAL_WIDTH = get_terminal_size()[0]

STYLE = {
    'pad': '=',
    'col_middle': '\033[1;34m',     # Bold blue
    'col_padding': '\033[0;34m',    # Blue
    'col_highlight': '\033[1;31m',  # Bold red
    'col_end': '\033[0m',
    'date_format': '%a %d %b %Y %H:%M',
}


def _get_header(entry, width):
    '''Return a colored header string padded to the correct width.'''

    # Date of entry in the middle
    middle = ' {0:{date_format}} '.format(entry.date, **STYLE)
    
    # Entry id on the right
    len_right = (width - len(middle))//2
    right = '{pad}{0}{pad}'.format(entry.id, **STYLE)
    right = '{0:{pad}>{1}}'.format(right, len_right, **STYLE)

    # Wordcount on the left
    len_left = width - len(middle) -len(right)
    left = '{pad}{0} words{pad}'.format(entry.wordcount, **STYLE)
    left = '{0:{pad}<{1}}'.format(left, len_left, **STYLE)

    # Add colours to each section and concatenate
    left = '{col_padding}{0}{col_end}'.format(left, **STYLE)
    middle = '{col_middle}{0}{col_end}'.format(middle, **STYLE)
    right = '{col_padding}{0}{col_end}'.format(right, **STYLE)

    return left + middle + right


def _gen_wrapped(lines, width):
    wrapper = TextWrapper(width=width)
    for line in lines:
        yield wrapper.fill(line)

def _gen_highlighted(lines, search_terms):
    pattern = '(' + '|'.join(search_terms) + ')'
    repl = r'{col_highlight}\1{col_end}'.format(**STYLE)
    re_obj = re.compile(pattern, re.I)

    for line in lines:
        yield re_obj.sub(repl, line)


def formatted(entry, search_terms=None, width=TERMINAL_WIDTH):
    '''Return the text of entry wrapped to width with a header.'''

    lines = entry.text.splitlines()
    lines = _gen_wrapped(lines, width-1)
    if search_terms and len(search_terms)>0:
        lines = _gen_highlighted(lines, search_terms)

    header = _get_header(entry, width)

    return header + '\n' + '\n'.join(lines) + '\n\n'


def display_entries(entries, display_command, search_terms=None):
    '''Open a separate process to display the given entries to the user.'''

    less_process = Popen(display_command, stdin=PIPE, shell=True)

    try:
        for entry in entries:
            less_process.stdin.write(bytes(formatted(entry, search_terms), 'UTF-8'))
        less_process.stdin.close()
        less_process.wait()

    except BrokenPipeError:
        pass  # Less process closed by user (hopefully) so stop quietly
