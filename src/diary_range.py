import os
import datetime
import re
import subprocess

DEFAULT_EDITOR_EXISTING = 'vim "+syntax off" "+set spell" "+set nonumber" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
DEFAULT_EDITOR_NEW = DEFAULT_EDITOR_EXISTING + ' "+startinsert"'

class Entry():

    _filename_re = re.compile(r'^diary-([0-9]+)-([a-zA-Z0-9_-]+)\.txt$')

    def __init__(self, *path_components):
        self._pathname = os.path.join(*path_components)
        match = Entry._filename_re.match(os.path.basename(self._pathname))
        self._timestamp, self._device_name = match.groups()

    @property
    def date(self):
        return datetime.datetime.fromtimestamp(int(self._timestamp))

    @property
    def wordcount(self):
        return len(re.findall(r'\S+', self.text))

    @property
    def text(self):
        with open(self._pathname) as f:
            return f.read()

    def contains(self, search_string):
        return re.search(search_string, self.text, re.I)

    def command_line_edit(self,
                          editor_existing=DEFAULT_EDITOR_EXISTING,
                          editor_new=DEFAULT_EDITOR_NEW):

        directory = os.path.dirname(self._pathname)
        if not os.path.exists(directory):
            os.makedirs(directory)

        editor = editor_existing if os.path.isfile(self._pathname) else editor_new
        subprocess.call('{} "{}"'.format(editor, self._pathname), shell=True)
        


class Helper():

    def __init__(self, dir_base):
        #TODO check that dir exists, if not create it
        #TODO normalise/absolutise path?
        self.dir_base = dir_base
        self.dir_entries = os.path.realpath(os.path.expanduser(os.path.expandvars(
                os.path.join(dir_base, 'data', 'entries'))))

    def new_entry(self, timestamp=None, device_name='unknown'):
        '''Return a new (not currently existing) entry.
        
        Note that the directory structure may not exist.'''

        entry_date = datetime.datetime.today() if timestamp is None else \
                     datetime.datetime.fromtimestamp(timestamp)
        
        timestamp = entry_date.strftime('%s')
        month = entry_date.strftime('%Y-%m')

        filename = 'diary-{}-{}.txt'.format(timestamp, device_name)

        return Entry(self.dir_entries, month, filename)

    def get_entries(self, descending=False, min_date=None, max_date=None):
        '''Return an generator over all entries.'''

        for month in sorted(os.listdir(self.dir_entries), reverse=descending):
            for filename in sorted(os.listdir(os.path.join(self.dir_entries, month)), 
                                   reverse=descending):

                entry = Entry(self.dir_entries, month, filename)

                if min_date is not None and entry.date < min_date:
                    if descending: break 
                    else: continue
                    
                if max_date is not None and entry.date > max_date:
                    if descending: continue 
                    else: break

                yield entry

    def search_entries(self, *search_terms, **kwargs):
        '''Filter entries by search terms.'''
        for entry in self.get_entries(**kwargs):
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
