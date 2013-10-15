#!/usr/bin/env python3

import argparse
from itertools import islice
import diary_range
import diary_list

# TODO Add search term logging and additional command line options from 
#      previous diary-search bash script. 

parser = argparse.ArgumentParser(description='Search for words or tags.')

parser.add_argument('-a', '--all', action='store_const', 
                    dest='max', const=None, default=argparse.SUPPRESS,
                    help='')

parser.add_argument('-m', '--max', action='store', type=int, default=40,
                    help='')

parser.add_argument('-t', '--tags', action='store_const', 
                    dest='mode', const='tags',
                    help='')

parser.add_argument('-w', '--words', action='store_const', 
                    dest='mode', const='words',
                    help='')

parser.add_argument('search_terms', nargs='+',
                    help='')

args = parser.parse_args()

search_strings = []

for search_term in args.search_terms:
    if args.mode is None or args.mode == 'tags':
        search_strings.append(r'#{}\S*\>'.format(search_term))

    elif args.mode == 'words':
        search_strings.append(search_term)

search_string = '\|'.join(search_strings)

entries = diary_range.filter_entries(search_string)
entries = islice(entries, args.max)

diary_list.display_entries(entries)
