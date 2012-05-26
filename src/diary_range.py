#!/usr/bin/env python3
# Script for finding the names of diary entries.

# Should be able to return filenames corresponding to specific timestamps, 
# ranges of entries, single entries and new entries (with a given date). 

import os
from os.path import realpath, join, basename, dirname, exists, isfile, getmtime
import math
import datetime
import time
import argparse
import re
from subprocess import check_output, call
from itertools import islice
import sys
import shelve

# Open cache shelf.
cache_path = os.environ['dir_entries_cache']
if not exists(cache_path):
    os.makedirs(cache_path)
cache_shelf = shelve.open(cache_path + '/range-cache', writeback=False)

class CachedEntry():
    '''Namespace for storing cached entry attributes.'''
    def __init__(self, entry):
        self.mtime = entry.getmtime()

def cached(func):
    '''Cache the results of a function, recalculate when cache is outdated.'''

    def wrapper(self):
        cached_entry = cache_shelf.get(self.timestamp, None)

        if cached_entry is None or cached_entry.mtime != self.getmtime():
            cached_entry = CachedEntry(self)
            
        if not hasattr(cached_entry, func.__name__):
            result = func()
            setattr(cached_entry, func.__name__, result) 
            cache_shelf[self.timestamp] = cached_entry

        return getattr(cached_entry, func.__name__)

    return wrapper

class Entry():
    '''Encapsulates entry manipulation functionality.'''

    _filename_re = re.compile(
            r'^diary-(-?[0-9]+)-([a-zA-Z0-9_][a-zA-Z0-9_-]*)\.([a-z]+)$')

    def __init__(self, *path_components):
        self.pathname = realpath(join(*path_components))
        match = Entry._filename_re.match(basename(self.pathname))
        self.timestamp, self.device_name, self.extension = match.groups()

    def mkdir(self):
        '''Create the entry's base directory (if it does not exist).'''
        directory = dirname(self.pathname)
        if not exists(directory):
            os.makedirs(directory)

    def exists(self):
        '''Return True if the entry exists.'''
        return isfile(self.pathname)

    def contains(self, search_string):
        '''Return True if the entry contains the given search string.'''
        command = 'grep -qi "{}" "{}"'.format(search_string, self.pathname)
        return call(command, shell=True) == 0

    def getmtime(self):
        '''Return the timestamp when the entry was last modified.'''
        if not self.exists(): 
            return None
        if 


    def tags(self):
        '''Return a list of all tags occurring in the entry text.'''
        # TODO add caching

        command = r'grep -o "#\S\+\b" "{}" || true'.format(self.pathname)
        matches = check_output(command, shell=True, universal_newlines=True)

        matches = matches.split('\n')
        matches = [ match.lstrip('#').rstrip() for match in matches ]
        matches = [ match for match in matches if len(match)>0 ]

        return matches


# Load constants that have previously been sourced and exported in bash.
# TODO: change this to use a better way to store and load them. 
dir_entries = os.environ['dir_entries']
device_name = os.environ['device_name']

# TODO move this to the Entry class definition. 
def new_entry(timestamp=None, device_name=device_name):
    '''Return a new (not currently existing) entry.
    
    Note that the directory structure may not exist.'''

    timestamp = int(time.time()) if timestamp is None else int(timestamp)
    month = time.strftime('%Y-%m', time.localtime(timestamp))
    filename = 'diary-{}-{}.txt'.format(timestamp, device_name)

    return [Entry(dir_entries, month, filename)]

def _find_with_command(command):
    results = check_output(command, shell=True, universal_newlines=True)
    return [ Entry(result) for result in results.split('\n') if len(result)>0 ]

def find_by_timestamp(timestamp):
    '''Returns any entries with the given timestamp.'''
    command = 'find "{}" -iname "*-{}-*"'.format(dir_entries, timestamp)
    return _find_with_command(command)

def modified_since(timestamp=0):
    '''Returns all entries last modified after the given timestamp.'''
    command = 'find "{}" -type f -newermt @{}'.format(dir_entries, timestamp)
    return _find_with_command(command)

def walk_all_entries(reverse=False):
    '''Iterates over all entries.'''
    for month in sorted(os.listdir(dir_entries), reverse=reverse):
        for filename in sorted(os.listdir(join(dir_entries, month)), 
                               reverse=reverse):
            yield Entry(dir_entries, month, filename)

def range_of_entries(slice_args):
    '''Returns all entries in the given range.'''

    start, stop, step = slice_args

    # If start, stop and step are all positive (or None) then use islice.
    if (step is None or step > 0) and \
       (start is None or start >= 0) and \
       (stop is None or stop >=0):
        return islice(walk_all_entries(), start, stop, step)

    # If start, stop and step are all negative (or None) then use islice.
    elif (step is not None and step < 0) and \
         (start is None or start < 0) and \
         (stop is None or stop < 0):
        start = None if start is None else -1*start
        stop = None if stop is None else -1*stop
        step = None if step is None else -1*step
        return islice(walk_all_entries(reverse=True), start, stop, step)

    # If there is a mixture of positives and negatives then use regular slice.
    else:
        return list(walk_all_entries())[start:stop:step]

def single_entry(index):
    '''Return a single entry at the given index.'''
    if index >= 0:
        return range_of_entries((index, index+1, 1))
    else:
        return range_of_entries((None if index==-1 else index+1, index, -1))

def filter_entries(search_string, entries=None):
    '''Filter entries by presence of the (regular expression) search string.

    If entries is None then search all entries in reverse order.'''

    if entries is None: 
        entries = walk_all_entries(reverse=True)

    for entry in entries:
        if entry.contains(search_string):
            yield entry


def range_type(string, range_re=re.compile(
            r'^([+_-]?[0-9]+)?:([+_-]?[0-9]+)?(?::([+_-]?[0-9]+))?$')):

    '''Returns (start, stop, step) for the given slice.'''
    match = range_re.match(string)
    if not match: 
        raise argparse.ArgumentTypeError('invalid range')
    
    start, stop, step = match.groups()
    start = None if start is None else int(start.replace('_', '-'))
    stop = None if stop is None else int(stop.replace('_', '-'))
    step = None if step is None else int(step.replace('_', '-'))

    return (start, stop, step)

class QueueAction(argparse.Action):
    '''Appends (dest, args) pairs to 'queue' in the returned Namespace.'''
    def __call__(self, parser, namespace, value, option_string=None):
        if not hasattr(namespace, 'queue'): 
            namespace.queue = []
        namespace.queue.append( (self.dest, value) )


parser = argparse.ArgumentParser(description='Get entry filenames.')

parser.add_argument('-n', '--new', nargs='?', type=int, 
                    dest='new_entry', metavar='NEW',
                    help='new entry with given timestamp', 
                    action=QueueAction, default=argparse.SUPPRESS)

parser.add_argument('-r', '--range', type=range_type,
                    dest='range_of_entries', metavar='SLICE',
                    help='range of entries',
                    action=QueueAction, default=argparse.SUPPRESS)
                    
parser.add_argument('-i', '--index', type=int,
                    dest='single_entry', metavar='INDEX',
                    help='single entry at INDEX',
                    action=QueueAction, default=argparse.SUPPRESS)
                    
parser.add_argument('-t', '--timestamp', type=int,
                    dest='find_by_timestamp', metavar='TIMESTAMP',
                    help='all entries created on TIMESTAMP',
                    action=QueueAction, default=argparse.SUPPRESS)

parser.add_argument('-m', '--modified', type=int,
                    dest='modified_since', metavar='MODIFIED',
                    help='all entries modified since MODIFIED',
                    action=QueueAction, default=argparse.SUPPRESS)

parser.add_argument('-s', '--search', type=str,
                    dest='filter_entries', metavar='SEARCH',
                    help='all entries containing SEARCH',
                    action=QueueAction, default=argparse.SUPPRESS)


def process_args():
    '''Return a list of all entries specified by the command line args.'''

    args = parser.parse_args()

    if hasattr(args, 'queue'):
        for func_name, value in args.queue:
            for entry in globals()[func_name](value):
                yield entry


# If running as script then print the filenames of all entries. 
if __name__ == '__main__':

    for entry in process_args():
        print(entry.pathname)
