import argparse
import subprocess
import diary_range
from presenter import display_entries

PROGRAM_NAME = 'diary'
VERSION_NUMBER = '2.0.0'


# Try to load fuzzy date parsing if it is installed, otherwise use strptime
try:
    import dateutil.parser
    def custom_date(date_string):
        #TODO use a reference date (or two) so that today's date doesn't fill in the unspecified bits
        #TODO add an `--on` option which takes one date and then calculates the highest and lowest dates
        #     which that could apply to and passes them to the maximum and minimum date fields
        return dateutil.parser.parse(date_string, fuzzy=True)

except:
    import datetime
    def custom_date(date_string):
        return datetime.datetime.strptime(date_string, '%Y-%m-%d')


def edit_command(conn, entry_id, **kwargs):
    entry = conn.find_by_id(entry_id) if entry_id else conn.most_recent_entry()
    entry.command_line_edit()

def new_command(conn, date, **kwargs):
    entry = conn.new_entry(date)
    entry.command_line_edit()

def search_command(conn, search_terms, descending, after, before, **kwargs):
    entries = conn.search_entries(*search_terms, descending=descending, min_date=after, max_date=before)
    display_entries(entries, search_terms)

def wordcount_command(conn, group_by, descending, after, before, **kwargs):
    #TODO clean this up a bit and move to a separate module? Move to the presenter module?
    if group_by is None: group_by = 'Total'
    entries = conn.get_entries(descending=descending, min_date=after, max_date=before)
    wordcounts = {}
    entry_counts = {}

    for entry in entries:
        group = entry.date.strftime(group_by)
        if group not in wordcounts:
            wordcounts[group] = 0
            entry_counts[group] = 0
        wordcounts[group] += entry.wordcount
        entry_counts[group] += 1

    if len(wordcounts)>1:
        wordcounts['Total'] = sum(wordcounts.values())
        entry_counts['Total'] = sum(entry_counts.values())

    longest_wc = max(len(str(wordcount)) for wordcount in wordcounts.values())
    longest_ec = max(len(str(entry_count)) for entry_count in entry_counts.values())
    longest_group = max(len(group) for group in wordcounts.keys())

    format_string = '{:>'+str(longest_group)+'}:  {:>'+str(longest_wc)+'} words,  {:>'+str(longest_ec)+'} entries'

    for group in sorted(wordcounts.keys(), reverse=descending):
        print(format_string.format(group, wordcounts[group], entry_counts[group]))


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

#TODO edit and new seem to be almost identical, combine them into one? Ditto for search and list
#TODO add help text for optional arguments
subparser = subparsers.add_parser('edit')
subparser.add_argument('entry_id', nargs='?')
subparser.set_defaults(func=edit_command)

subparser = subparsers.add_parser('new')
subparser.add_argument('date', type=custom_date, nargs='?')
subparser.set_defaults(func=new_command)


# The 'list' command is essentially identical to the 'search' command 
# except that it specifies search terms with a different syntax
subparser = subparsers.add_parser('list', parents=[filter_parser])
subparser.add_argument('--search', action='append', dest='search_terms', metavar='SEARCH_TERM')
subparser.set_defaults(func=search_command, search_terms=[])

subparser = subparsers.add_parser('search', parents=[filter_parser])
subparser.add_argument('search_terms', nargs='*')
subparser.set_defaults(func=search_command)


subparser = subparsers.add_parser('wordcount', parents=[filter_parser], aliases=['wc'])
subparser.add_argument('-y', '--year', action='store_const', const='%Y', dest='group_by')
subparser.add_argument('-m', '--month', action='store_const', const='%Y-%m', dest='group_by')
subparser.add_argument('-g', '--group-by', dest='group_by', metavar='DATE_FORMAT')
#TODO default to ascending order without breaking the regular default
subparser.set_defaults(func=wordcount_command)


def process_args():
    args = parser.parse_args()
    if hasattr(args, 'func'):
        conn = diary_range.connect(args.base)
        args.func(conn, **vars(args))
    else:
        parser.print_usage()

if __name__ == '__main__':
    process_args()
