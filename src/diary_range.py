import os
from os.path import realpath, join, basename, expandvars, expanduser
#TODO only use datetime
import time
import datetime
import re
import subprocess

DEFAULT_EDITOR_EXISTING = 'vim "+syntax off" "+set spell" "+set nonumber" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
DEFAULT_EDITOR_NEW = DEFAULT_EDITOR_EXISTING + ' "+startinsert"'

class Entry():

    _filename_re = re.compile(r'^diary-([0-9]+)-([a-zA-Z0-9_-]+)\.([a-z]+)$')

    def __init__(self, *path_components):
        self.pathname = join(*path_components)
        match = Entry._filename_re.match(basename(self.pathname))
        self.timestamp, self.device_name, self.extension = match.groups()

    @property
    def date(self):
        return datetime.datetime.fromtimestamp(int(self.timestamp))

    @property
    def wordcount(self):
        return len(re.findall(r'\S+', self.text))

    @property
    def text(self):
        with open(self.pathname) as f:
            return f.read()

    def contains(self, search_string):
        return re.search(search_string, self.text, re.I)

    def command_line_edit(self,
                          editor_existing=DEFAULT_EDITOR_EXISTING,
                          editor_new=DEFAULT_EDITOR_NEW):

        directory = os.path.dirname(self.pathname)
        if not os.path.exists(directory):
            os.makedirs(directory)

        editor = editor_existing if os.path.isfile(self.pathname) else editor_new
        subprocess.call('{} "{}"'.format(editor, self.pathname), shell=True)
        


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

                if min_date is not None and entry.date < min_date:
                    if descending: break 
                    else: continue
                    
                if max_date is not None and entry.date > max_date:
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
        results = subprocess.check_output(command, shell=True, universal_newlines=True)
        return ( Entry(result) for result in results.split('\n') if len(result)>0 )

    def find_by_timestamp(self, timestamp):
        '''Returns any entries with the given timestamp.'''
        command = 'find "{}" -iname "*-{}-*"'.format(self.dir_entries, timestamp)
        return self._find_with_command(command)


def connect(dir_base):
    return Helper(dir_base)
