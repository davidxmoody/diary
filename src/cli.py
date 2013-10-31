import argparse
import diary_range
from presenter import display_entries
from fuzzydate import custom_date

PROGRAM_NAME = 'diary'
VERSION_NUMBER = '2.0.0'


# Filter options parser (shared between commands processing multiple entries)
filter_parser = argparse.ArgumentParser(add_help=False)
filter_parser.add_argument('--before', type=custom_date, metavar='DATE')
filter_parser.add_argument('--after', type=custom_date, metavar='DATE')
filter_parser.add_argument('--asc', action='store_false', dest='descending')
filter_parser.add_argument('--desc', action='store_true', dest='descending')
filter_parser.set_defaults(descending=True)


# Setup main parser
parser = argparse.ArgumentParser(description='') 
parser.add_argument('--version', action='version', 
        version='{} {}'.format(PROGRAM_NAME, VERSION_NUMBER))
parser.add_argument('-b', '--base', help='path to base folder')


# Setup subparsers for each command
subparsers = parser.add_subparsers()

#TODO add help text for optional arguments

# The 'edit' command edits the most recent entry or the entry specified by entry_id
def edit_command(conn, entry_id, **kwargs):
    entry = conn.find_by_id(entry_id) if entry_id else conn.most_recent_entry()
    entry.command_line_edit()

subparser = subparsers.add_parser('edit')
subparser.add_argument('entry_id', nargs='?')
subparser.set_defaults(func=edit_command)


# The 'new' command creates and edits a new entry with the current date or the given date
def new_command(conn, date, **kwargs):
    entry = conn.new_entry(date)
    entry.command_line_edit()

subparser = subparsers.add_parser('new')
subparser.add_argument('date', type=custom_date, nargs='?')
subparser.set_defaults(func=new_command)


#TODO make list an actual alias to search, also add the --search option to the general filter?
#TODO stop using the shared searching filter?
# The 'search' command displays all entries containing all of the given search_terms
def search_command(conn, search_terms, descending, after, before, **kwargs):
    entries = conn.search_entries(*search_terms, descending=descending, min_date=after, max_date=before)
    display_entries(entries, search_terms)

subparser = subparsers.add_parser('search', parents=[filter_parser])
subparser.add_argument('search_terms', nargs='*')
subparser.set_defaults(func=search_command)

# The 'list' command is identical to the search command but with slightly different syntax
subparser = subparsers.add_parser('list', parents=[filter_parser])
subparser.add_argument('--search', action='append', dest='search_terms', metavar='SEARCH_TERM')
subparser.set_defaults(func=search_command, search_terms=[])


# The 'wordcount' command pretty prints wordcount statistics
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

    results = [ (group, wordcounts[group], entry_counts[group]) for group in sorted(wordcounts.keys()) ]

    if len(results)>1:
        results.append( ('Total', sum(wordcounts.values()), sum(entry_counts.values())) )
    
    max_lengths = { 'len_group': max( len(str(result[0])) for result in results ),
                    'len_wc': len(str(results[-1][1])),
                    'len_ec': len(str(results[-1][2])) }

    format_string = '{0:>{len_group}}:  {1:>{len_wc}} words,  {2:>{len_ec}} entries'

    for result in results:
        print(format_string.format(*result, **max_lengths))


subparser = subparsers.add_parser('wordcount', aliases=['wc'])
subparser.add_argument('-y', '--year', action='store_const', const='%Y', dest='group_by')
subparser.add_argument('-m', '--month', action='store_const', const='%Y-%m', dest='group_by')
subparser.add_argument('-w', '--weekday', action='store_const', const='%u %a', dest='group_by')
subparser.add_argument('-g', '--group-by', dest='group_by', metavar='DATE_FORMAT')
subparser.set_defaults(func=wordcount_command)


# Process args and run the corresponding function
def process_args():
    args = parser.parse_args()
    if hasattr(args, 'func'):
        conn = diary_range.connect(args.base)
        args.func(conn, **vars(args))
    else:
        parser.print_usage()

if __name__ == '__main__':
    process_args()
