from subprocess import check_output, Popen, PIPE
import textwrap
import time
import re

PAD_CHAR = '='
COLOR_MIDDLE = '\033[1;34m'     # Bold blue
COLOR_PADDING = '\033[0;34m'    # Blue
COLOR_HIGHLIGHT = '\033[1;31m'  # Bold red
COLOR_END = '\033[0m'

DATE_FORMAT = '%a %d %b %Y %H:%M'
#TODO add a try clause which defaults to 70 if this fails
TERMINAL_WIDTH = int(check_output('tput cols', shell=True).strip())


def get_header(entry, width):
    '''Return a colored header string padded to the correct width.'''

    left = PAD_CHAR + '{} words'.format(entry.wordcount)
    right = entry.id + PAD_CHAR
    middle = ' {} '.format(entry.date.strftime(DATE_FORMAT))

    padding_left = PAD_CHAR * int(width/2 - len(left) - len(middle)/2)
    padding_right = PAD_CHAR * (width - len(left) - 
                        len(padding_left) - len(middle) - len(right))

    return COLOR_PADDING +     left      + padding_left + COLOR_END + \
           COLOR_MIDDLE  +            middle            + COLOR_END + \
           COLOR_PADDING + padding_right +    right     + COLOR_END

def highlighted(text, search_terms):
    #TODO reuse the same re_obj between paragraphs
    #TODO fix bug where searching with word boundaries doesn't highlight the term
    if len(search_terms)==0: return text
    re_string = '(' + '|'.join(re.escape(term) for term in search_terms) + ')'
    re_obj = re.compile(re_string, re.I)
    repl = r'{}\1{}'.format(COLOR_HIGHLIGHT, COLOR_END)
    return re_obj.sub(repl, text)

def _gen_formatted(entry, search_terms, width):
    '''Return a generator over the formatted, wrapped paragraphs of an entry.'''

    yield get_header(entry, width)

    wrapper = textwrap.TextWrapper(width=width)

    for line in entry.text.splitlines():
        wrapped_para = wrapper.fill(line)
        highlighted_para = highlighted(wrapped_para, search_terms)
        yield highlighted_para

def formatted(entry, search_terms, width=TERMINAL_WIDTH):
    '''Return the text of entry wrapped to width with a header.'''
    return '\n'.join(_gen_formatted(entry, search_terms, width)) + '\n\n'

def display_entries(entries, search_terms=[]):
    '''Open a less pipe to display the given entries to the user.'''

    less_process = Popen('less -R', stdin=PIPE, shell=True)

    try:
        for entry in entries:
            less_process.stdin.write(bytes(formatted(entry, search_terms), 'UTF-8'))
        less_process.stdin.close()
        less_process.wait()

    except BrokenPipeError:
        # Less process closed by user (hopefully) so stop quietly
        pass
