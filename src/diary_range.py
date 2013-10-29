import os
from os.path import realpath, join, basename, dirname, exists, isfile, getmtime
from os.path import expandvars, expanduser
#TODO only use datetime
import time
import datetime
import re
from subprocess import check_output, call
from itertools import islice

class Entry():
    '''Encapsulates entry manipulation functionality.'''

    _filename_re = re.compile(
            r'^diary-([0-9]+)-([a-zA-Z0-9_-]+)\.([a-z]+)$')

    #TODO rewrite this to use the @property decorator instead of functions
    def __init__(self, *path_components):
        self.pathname = join(*path_components)
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

    def get_date(self):
        return datetime.datetime.fromtimestamp(int(self.timestamp))

    def contains(self, search_string):
        '''Return True if the entry contains the given search string.'''
        command = 'grep -qi "{}" "{}"'.format(search_string, self.pathname)
        return call(command, shell=True) == 0

    def wordcount(self):
        '''Return the number of space separated words in the entry.'''
        command = 'wc -w < "{}"'.format(self.pathname)
        return int(check_output(command, shell=True).strip())

    def text(self):
        with open(self.pathname) as f:
            return f.read()


class Helper():

    def __init__(self, dir_base):
        #TODO check that dir exists, if not create it
        #TODO normalise/absolutise path?
        self.dir_base = dir_base
        self.dir_entries = realpath(expanduser(expandvars(
                join(dir_base, 'data', 'entries'))))

    def new_entry(self, timestamp=None, device_name='unknown'):
        '''Return a new (not currently existing) entry.
        
        Note that the directory structure may not exist.'''

        timestamp = int(time.time()) if timestamp is None else int(timestamp)
        month = time.strftime('%Y-%m', time.localtime(timestamp))
        filename = 'diary-{}-{}.txt'.format(timestamp, device_name)

        return Entry(self.dir_entries, month, filename)

    def get_entries(self, descending=False, min_date=None, max_date=None):
        '''Return an generator over all entries.'''

        for month in sorted(os.listdir(self.dir_entries), reverse=descending):
            for filename in sorted(os.listdir(join(self.dir_entries, month)), 
                                   reverse=descending):

                entry = Entry(self.dir_entries, month, filename)

                if min_date is not None and entry.get_date() < min_date:
                    if descending: break 
                    else: continue
                    
                if max_date is not None and entry.get_date() > max_date:
                    if descending: continue 
                    else: break

                yield entry

    def search_entries(self, *search_terms, entries=None, **kwargs):
        '''Filter entries by search terms.'''
        if entries is None: entries = self.get_entries(**kwargs)

        for entry in entries:
            if all(entry.contains(term) for term in search_terms):
                yield entry

    def _find_with_command(self, command):
        results = check_output(command, shell=True, universal_newlines=True)
        return ( Entry(result) for result in results.split('\n') if len(result)>0 )

    def find_by_timestamp(self, timestamp):
        '''Returns any entries with the given timestamp.'''
        command = 'find "{}" -iname "*-{}-*"'.format(self.dir_entries, timestamp)
        return self._find_with_command(command)


def connect(dir_base):
    return Helper(dir_base)
