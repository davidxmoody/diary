from argparse import ArgumentParser
from diary_range import connect
from presenter import display_entries
from fuzzydate import custom_date

from web.exporter import export_command

__version__ = '2.0.1'


# SETUP MAIN PARSER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

parser = ArgumentParser(
    description='A program for writing and viewing a personal diary')

parser.add_argument('--version', action='version', 
    version='%(prog)s {}'.format(__version__))

parser.add_argument('-b', '--base', default='~/.diary', 
    help='path to base folder')

subparsers = parser.add_subparsers(title='subcommands')



# EDIT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def edit_command(conn, entry_id, **kwargs):
    entry = conn.find_by_id(entry_id) if entry_id else conn.most_recent_entry()
    if entry:
        entry.command_line_edit()
    else:
        print('No entry to edit', 
              'for entry_id: {}'.format(entry_id) if entry_id else '')

subparser = subparsers.add_parser('edit',
    description='Open Vim to edit the most recent entry '
                'or the entry specified by entry_id',
    help='edit the most recent entry or a specified entry')

subparser.add_argument('entry_id', nargs='?', 
    help='entry id of the form "$timestamp-$device_name"')

subparser.set_defaults(func=edit_command)



# NEW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def new_command(conn, date, **kwargs):
    entry = conn.new_entry(date)
    entry.command_line_edit()

subparser = subparsers.add_parser('new',
    description='Open Vim to edit a new entry',
    help='create a new entry')

subparser.add_argument('date', type=custom_date, nargs='?', 
    help='date of the new entry (defaults to now)')

subparser.set_defaults(func=new_command)



# SEARCH ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def search_command(conn, search_terms, descending, after, before, **kwargs):
    entries = conn.search_entries(*search_terms, descending=descending, 
                                  min_date=after, max_date=before)
    display_entries(entries, search_terms)

subparser = subparsers.add_parser('search', aliases=['list'],
    description='Display entries containing all of the given search terms',
    help='display all entries, with optional search filter')

subparser.add_argument('search_terms', nargs='*',
    help='any number of regular expressions to search for')

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

def wordcount_command(conn, group_by, **kwargs):
    if group_by is None: group_by = 'Total'
    wordcounts = {}
    entry_counts = {}

    for entry in conn.get_entries():
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
group_by.add_argument('-w', '--weekday', action='store_const', const='%u %a', 
    dest='group_by', help='group by weekday')
group_by.add_argument('-g', '--group-by', metavar='DATE_FORMAT',
    dest='group_by', help='format entry dates with DATE_FORMAT and combine '
                          'wordcount totals for all entries which have the '
                          'same formatted date, e.g. "%%Y-%%m-%%d"')

subparser.set_defaults(func=wordcount_command)



# EXPORT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# export_command function is imported from the web.exporter module

subparser = subparsers.add_parser('export',
    description='Export static web pages containing diary entries',
    help='export diary as static web pages')

subparser.set_defaults(func=export_command)



# PROCESS ARGS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def process_args():
    args = parser.parse_args()
    if hasattr(args, 'func'):
        conn = connect(args.base)
        args.func(conn, **vars(args))
    else:
        parser.print_usage()

if __name__ == '__main__':
    process_args()