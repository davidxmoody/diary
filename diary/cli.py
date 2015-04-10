from argparse import ArgumentParser
from diary.database import connect
from diary.presenter import display_entries
from diary.utils import custom_date
from diary.generator import generate_command
import logging
import re
import os

__version__ = '2.2.0'

try:
    # Strip non- word or dash characters from device name
    DEVICE_NAME = re.sub(r'[^\w-]', '', os.uname().nodename)
except:
    DEVICE_NAME = 'unknown'


# SETUP MAIN PARSER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

parser = ArgumentParser(
    description='A program for writing and viewing a personal diary')

parser.add_argument('--version', action='version', 
    version='%(prog)s {}'.format(__version__))

parser.add_argument('-b', '--base', default=os.path.expandvars('$HOME/.diary'),
    help='path to base folder (defaults to `~/.diary`)')

subparsers = parser.add_subparsers(title='subcommands')



# EDIT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def edit_command(conn, search_terms, entry_id, editor, message, **kwargs):
    if entry_id:
        entry = conn.find_by_id(entry_id) if entry_id else conn.most_recent_entry()
    else:
        entry = conn.search_entries(*search_terms, descending=True).__next__()
    if entry:
        if message is not None:
            entry.text = message
        else:
            entry.command_line_edit(editor)
    else:
        print('No entry to edit')

subparser = subparsers.add_parser('edit',
    description='Open Vim to edit the most recent entry',
    help='edit the most recent entry or a specified entry')

subparser.add_argument('search_terms', nargs='*',
    help='any number of regular expressions to search for')
subparser.add_argument('--entry-id', 
    help='entry id of the form "$timestamp-$device_name"')
subparser.add_argument('-e', '--editor', default='vim',
    help='editor to write the entry with (defaults to `vim`)')
subparser.add_argument('-m', '--message', 
    help='directly set the text of the entry to MESSAGE')

subparser.set_defaults(func=edit_command)



# NEW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def new_command(conn, date, editor, message, device_name, **kwargs):
    entry = conn.new_entry(date, device_name)
    if message is not None:
        entry.text = message
    else:
        entry.command_line_edit(editor)

subparser = subparsers.add_parser('new',
    description='Open Vim to edit a new entry',
    help='create a new entry')

subparser.add_argument('-d', '--date', type=custom_date, 
    help='date of the new entry (defaults to now)')
subparser.add_argument('-e', '--editor', default='vim',
    help='editor to write the entry with (defaults to `vim`)')
subparser.add_argument('-m', '--message', 
    help='directly set the text of the entry to MESSAGE')
subparser.add_argument('--device-name', default=DEVICE_NAME, 
    help='name of the device the entry was created on ' + 
         '(defaults to `{}`)'.format(DEVICE_NAME))

subparser.set_defaults(func=new_command)



# SEARCH ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def search_command(conn, search_terms, descending, after, before, pipe_to, **kwargs):
    entries = conn.search_entries(*search_terms, descending=descending, 
                                  min_date=after, max_date=before)
    display_entries(entries, pipe_to, search_terms)

subparser = subparsers.add_parser('search', aliases=['list'],
    description='Display entries containing all of the given search terms',
    help='display all entries, with optional search filter')

subparser.add_argument('search_terms', nargs='*',
    help='any number of regular expressions to search for')

subparser.add_argument('--pipe-to', metavar='COMMAND', default='less -R',
    help='pipe output to the given command')

#TODO this is shared with wordcount script below, abstract it
subparser.add_argument('--before', type=custom_date, metavar='DATE',
    help='only show entries occurring before DATE')
subparser.add_argument('--after', type=custom_date, metavar='DATE',
    help='only show entries occurring after DATE')

sort_order = subparser.add_mutually_exclusive_group()
sort_order.add_argument('--asc', action='store_false', dest='descending',
    help='sort in ascending date order')
sort_order.add_argument('--desc', action='store_true', dest='descending',
    help='sort in descending date order')

subparser.set_defaults(func=search_command, descending=True)



# WORDCOUNT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def wordcount_command(conn, group_by, descending, after, before, **kwargs):
    if group_by is None: group_by = 'Total'
    wordcounts = {}
    entry_counts = {}

    for entry in conn.get_entries(descending=descending, min_date=after, 
                                                         max_date=before):
        group = entry.date.strftime(group_by)
        if group not in wordcounts:
            wordcounts[group], entry_counts[group] = 0, 0
        wordcounts[group] += entry.wordcount
        entry_counts[group] += 1

    results = [ (group, wordcounts[group], entry_counts[group]) 
                            for group in sorted(wordcounts.keys()) ]

    if len(results)>1:
        results.append( ('Total', sum(wordcounts.values()), 
                                  sum(entry_counts.values())) )

    if len(results)==0:
        results.append( ('Total', 0, 0) )
    
    max_lengths = {'len_group': max(len(str(result[0])) for result in results),
                   'len_wc': len(str(results[-1][1])),
                   'len_ec': len(str(results[-1][2]))}

    fmt_str = '{0:>{len_group}}:  {1:>{len_wc}} words,  {2:>{len_ec}} entries'

    for result in results:
        print(fmt_str.format(*result, **max_lengths))


subparser = subparsers.add_parser('wordcount', aliases=['wc'],
    description='Pretty print aggregated wordcount totals',
    help='print wordcount statistics')

group_by = subparser.add_mutually_exclusive_group()
group_by.add_argument('-y', '--year', action='store_const', const='%Y', 
    dest='group_by', help='group by year')
group_by.add_argument('-m', '--month', action='store_const', const='%Y-%m', 
    dest='group_by', help='group by month')
group_by.add_argument('-d', '--day', action='store_const', const='%Y-%m-%d', 
    dest='group_by', help='group by day')
group_by.add_argument('-w', '--weekday', action='store_const', const='%u %a', 
    dest='group_by', help='group by weekday')
group_by.add_argument('-g', '--group-by', metavar='DATE_FORMAT',
    dest='group_by', help='format entry dates with DATE_FORMAT and combine '
                          'wordcount totals for all entries which have the '
                          'same formatted date, e.g. "%%Y-%%m-%%d"')

subparser.add_argument('--before', type=custom_date, metavar='DATE',
    help='only show entries occurring before DATE')
subparser.add_argument('--after', type=custom_date, metavar='DATE',
    help='only show entries occurring after DATE')

sort_order = subparser.add_mutually_exclusive_group()
sort_order.add_argument('--asc', action='store_false', dest='descending',
    help='sort in ascending date order')
sort_order.add_argument('--desc', action='store_true', dest='descending',
    help='sort in descending date order')


subparser.set_defaults(func=wordcount_command)



# GENERATE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# generate_command is imported at the top

subparser = subparsers.add_parser('generate',
    description='Create a HTML representation of your diary',
    help='generate HTML diary')

subparser.add_argument('-o', '--out', 
    help='directory to place HTML (defaults to {your_base_dir}/html)')
subparser.add_argument('-w', '--watch', action='store_true',
    help='stay alive and update the HTML whenever entries change')
subparser.add_argument('-c', '--clean', action='store_true',
    help='remove out dir before generating')


subparser.set_defaults(func=generate_command)



# PROCESS ARGS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def process_args(arg_list=None):
    args = parser.parse_args(arg_list)
    if hasattr(args, 'func'):
        logging.basicConfig(level=logging.WARNING, 
                format='%(asctime)s - %(levelname)s - %(message)s',
                filename=os.path.join(args.base, '{}.log'.format(DEVICE_NAME)))

        conn = connect(args.base)
        args.func(conn, **vars(args))
    else:
        parser.print_usage()

if __name__ == '__main__':
    process_args()
