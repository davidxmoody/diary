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


#TODO Feature wishlist:

# - custom description and usage
# - set default diary dir (~/.diary)
# - create new entries with custom timestamp and/or device_name
# - case sensitivity options for search (both to enable and disable)
# - automatic (configurable) word boundaries added to search expressions (both to enable and disable)
# - add default device name selection (use the $HOSTNAME) 
# - aliases for commands (ls, wc, etc.)
# - allow the edit command to perform direct searches instead of only opening entries by timestamp?
# - print stats other than word and entry counts (tag counts, etc.)
# - print graphs instead of just summaries
# - command to print filenames of entries matching a search
# - implement diary chain script to calculate the maximum chain length of recurring tags (with customisable penalties for missing days)

# - user modifiable config file, located either in home dir or specific to diary dir (diary dir one should take precidence)
# - set default editors in config file
# - set default sort order and date ranges in config file
# - search options settable in config file
# - set device name in config file, ability to link to an external file for the device name
# - user configurable commands/aliases

#TODO re-write so that args is unpacked before being passed to the command functions

DEFAULT_EDITOR_EXISTING = 'vim "+syntax off" "+set spell" "+set nonumber" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
DEFAULT_EDITOR_NEW = DEFAULT_EDITOR_EXISTING + ' "+startinsert"'

def _edit_entry(entry, 
                editor_existing=DEFAULT_EDITOR_EXISTING,
                editor_new=DEFAULT_EDITOR_NEW):
    entry.mkdir()
    editor = editor_existing if entry.exists() else editor_new
    subprocess.call('{} "{}"'.format(editor, entry.pathname), shell=True)

def edit_command(args):
    # No timestamp given -> edit most recent entry
    if args.timestamp is None:
        entry = diary_range.connect(args.base).get_entries(descending=True).__next__()
        _edit_entry(entry)

    # Timestamp given -> try to edit that entry
    else:
        entries = list(diary_range.connect(args.base).find_by_timestamp(args.timestamp))
        if len(entries)==0:
            print("No entries found for timestamp: {}".format(args.timestamp))
        else:
            _edit_entry(entries[0])
        # Ignore the case where more than one entry exists with the given timestamp

def new_command(args):
    entry = diary_range.connect(args.base).new_entry(args.timestamp)
    _edit_entry(entry)

def list_command(args):
    entries = diary_range.connect(args.base).get_entries(descending=args.descending, min_date=args.after, max_date=args.before)
    display_entries(entries)

def search_command(args):
    entries = diary_range.connect(args.base).search_entries(*args.search_terms, descending=args.descending, min_date=args.after, max_date=args.before)
    display_entries(entries, args.search_terms)

def wordcount_command(args):
    #TODO clean this up a bit and move to a separate module?
    if args.group is None: args.group = 'Total'
    entries = diary_range.connect(args.base).get_entries(descending=args.descending, min_date=args.after, max_date=args.before)
    wordcounts = {}
    entry_counts = {}

    for entry in entries:
        group = entry.get_date().strftime(args.group)
        if group not in wordcounts:
            wordcounts[group] = 0
            entry_counts[group] = 0
        wordcounts[group] += entry.wordcount()
        entry_counts[group] += 1

    if len(wordcounts)>1:
        wordcounts['Total'] = sum(wordcounts.values())
        entry_counts['Total'] = sum(entry_counts.values())

    longest_wc = max(len(str(wordcount)) for wordcount in wordcounts.values())
    longest_ec = max(len(str(entry_count)) for entry_count in entry_counts.values())
    longest_group = max(len(group) for group in wordcounts.keys())

    format_string = '{:>'+str(longest_group)+'}:  {:>'+str(longest_wc)+'} words,  {:>'+str(longest_ec)+'} entries'

    for group in sorted(wordcounts.keys(), reverse=args.descending):
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
subparser.add_argument('timestamp', type=int, nargs='?')
subparser.set_defaults(func=edit_command)

subparser = subparsers.add_parser('new')
subparser.add_argument('timestamp', type=int, nargs='?')
subparser.set_defaults(func=new_command)

subparser = subparsers.add_parser('list', parents=[filter_parser])
#TODO make this option work
subparser.add_argument('--search', action='append', dest='search_terms', metavar='SEARCH_TERM')
subparser.set_defaults(func=list_command)

subparser = subparsers.add_parser('search', parents=[filter_parser])
subparser.add_argument('search_terms', nargs='+')
subparser.set_defaults(func=search_command)

subparser = subparsers.add_parser('wordcount', parents=[filter_parser], aliases=['wc'])
subparser.add_argument('-y', '--year', action='store_const', const='%Y', dest='group')
subparser.add_argument('-m', '--month', action='store_const', const='%Y-%m', dest='group')
subparser.add_argument('-g', '--group-by', dest='group', metavar='DATE_FORMAT')
#TODO default to ascending order without breaking the regular default
subparser.set_defaults(func=wordcount_command)


def process_args():
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_usage()

if __name__ == '__main__':
    process_args()
