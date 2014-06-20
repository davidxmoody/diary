import os
import datetime
import re
import subprocess

# Strip non- word or dash characters from device name
try:
    DEVICE_NAME = re.sub(r'[^\w-]', '', os.uname().nodename)
except:
    DEVICE_NAME = 'unknown'

#TODO Revert back this change, it shouldn't be in the diary program, it should
#     be a "custom editor" command
date = datetime.datetime.now().strftime('%F')
EDITOR_COMMAND = 'vim -w ~/.dbox/Dropbox/diary-data/vim-logs/vimdiary-{}.log'.format(date)


class Entry():

    _filename_re = re.compile(r'^diary-([0-9]+)-([a-zA-Z0-9_-]+)\.txt$')

    def __init__(self, *path_components):
        self._pathname = os.path.join(*path_components)
        match = Entry._filename_re.match(os.path.basename(self._pathname))
        self._timestamp, self._device_name = match.groups()

    @property
    def id(self):
        return '{}-{}'.format(self._timestamp, self._device_name)

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

    @property
    def mtime(self):
        return os.path.getmtime(self._pathname)

    def contains(self, search_string):
        return re.search(search_string, self.text, re.I)

    def command_line_edit(self):
        directory = os.path.dirname(self._pathname)
        if not os.path.exists(directory):
            os.makedirs(directory)
        subprocess.call('{} "{}"'.format(EDITOR_COMMAND, self._pathname), shell=True)
        


class connect():

    def __init__(self, dir_base):
        self.dir_base = dir_base
        self.dir_entries = os.path.realpath(os.path.expanduser(os.path.expandvars(
                os.path.join(dir_base, 'entries'))))

        if not os.path.exists(self.dir_entries):
            print('Creating diary database at: {}'.format(self.dir_base))
            os.makedirs(self.dir_entries)


    @property
    def dir_html(self):
        dir_html = os.path.realpath(os.path.expanduser(os.path.expandvars(
                os.path.join(self.dir_base, 'html'))))

        if not os.path.exists(dir_html):
            print('Creating html directory at: {}'.format(dir_html))
            os.makedirs(dir_html)

        return dir_html



    def new_entry(self, date=None, device_name=DEVICE_NAME):
        if date is None: date = datetime.datetime.today()

        timestamp = date.strftime('%s')
        month = date.strftime('%Y-%m')

        filename = 'diary-{}-{}.txt'.format(timestamp, device_name)

        return Entry(self.dir_entries, month, filename)


    def get_entries(self, descending=False, min_date=None, max_date=None):

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
        for entry in self.get_entries(**kwargs):
            if all(entry.contains(term) for term in search_terms):
                yield entry


    def most_recent_entry(self):
        try:
            return self.get_entries(descending=True).__next__()
        except StopIteration:
            return None

    
    def find_by_id(self, entry_id):
        for entry in self.get_entries():
            if entry.id == entry_id:
                return entry
