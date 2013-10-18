import argparse
#TODO move these imports to the functions where they are needed?
import subprocess
import diary_range
from presenter import display_entries

# Keywords I want to support now:
# - edit: open editor on most recent entry or specified entry
# - list: display recent entries or specified range of entries
# - new: open editor on a new entry
# - search: display entries matching a (complex) search query
# - wordcount (or stats): wordcount summary of all entries, other stats maybe
# - chain: calculate max chain length for tags in tag file (custom subtraction amount)
# - range (or filenames or something): print filenames in specified range (or make this an optional argument to list/search)
# - help: print help to stdout and exit
# - version: print version number

# Command line options I want to support:
# - -b for changing base dir


DEFAULT_EDITOR_EXISTING = 'vim "+syntax off" "+set spell" "+set nonumber" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
DEFAULT_EDITOR_NEW = DEFAULT_EDITOR_EXISTING + ' "+startinsert"'

def _edit_entry(entry, 
                editor_existing=DEFAULT_EDITOR_EXISTING,
                editor_new=DEFAULT_EDITOR_NEW):
    entry.mkdir()
    editor = editor_existing if entry.exists() else editor_new
    subprocess.call('{} "{}"'.format(editor, entry.pathname), shell=True)

def edit_command(args):
    print(args)
    #TODO select entry to edit with command line args and edit it

def new_command(args):
    entry = diary_range.connect(args.base).new_entry()
    _edit_entry(entry)

def list_command(args):
    #TODO pay attention to range args when choosing which entries to display
    entries = diary_range.connect(args.base).get_entries(descending=True)
    display_entries(entries)

def search_command(args):
    #TODO case sensitivity option
    entries = diary_range.connect(args.base).search_entries(*args.search_terms)
    display_entries(entries)


# Filter options parser
filter_parser = argparse.ArgumentParser(add_help=False)
#TODO implement filtering options next
# date range
# sort order
# modified since range
# search query (any combination of words and tags, or + and functionality)

#TODO add description and maybe custom usage?
parser = argparse.ArgumentParser(description='') 
#TODO add default base dir and device name
parser.add_argument('-b', '--base', help='path to base folder')
# version no
subparsers = parser.add_subparsers()

parser_edit = subparsers.add_parser('edit', parents=[filter_parser])
parser_edit.set_defaults(func=edit_command)

parser_new = subparsers.add_parser('new')
parser_new.set_defaults(func=new_command)

parser_list = subparsers.add_parser('list', parents=[filter_parser])
parser_list.set_defaults(func=list_command)

parser_search = subparsers.add_parser('search', parents=[filter_parser])
parser_search.add_argument('search_terms', nargs='+')
parser_search.set_defaults(func=search_command)


args = parser.parse_args()
args.func(args)
