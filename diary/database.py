import os
import datetime
import re
import subprocess
from markdown import markdown

# Strip non- word or dash characters from device name
try:
    DEVICE_NAME = re.sub(r'[^\w-]', '', os.uname().nodename)
except:
    DEVICE_NAME = 'unknown'


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
    def timestamp(self):
        #TODO add a timezone info property and decide what to do about the date property
        return self._timestamp

    @property
    def wordcount(self):
        return len(re.findall(r'\S+', self.text))

    @property
    def text(self):
        with open(self._pathname) as f:
            return f.read()

    @text.setter
    def text(self, text):
        self._mkdir()
        with open(self._pathname, 'w') as f:
            f.write(text)

    @property
    def html(self):
        tagged_text = re.sub(r'(#\w+)', r'<span class="hashtag">\1</span>', self.text)
        return markdown(tagged_text)

    @property
    def mtime(self):
        return os.path.getmtime(self._pathname)

    def contains(self, search_string):
        return re.search(search_string, self.text, re.I)

    def command_line_edit(self, command):
        self._mkdir()
        subprocess.call('{} "{}"'.format(command, self._pathname), shell=True)

    def _mkdir(self):
        directory = os.path.dirname(self._pathname)
        if not os.path.exists(directory):
            os.makedirs(directory)
        


class connect():

    def __init__(self, dir_base):
        self.dir_base = dir_base
        self.dir_entries = os.path.realpath(os.path.expanduser(os.path.expandvars(
                os.path.join(dir_base, 'entries'))))

        if not os.path.exists(self.dir_entries):
            #TODO put this into a log rather than printing it
            #print('Creating diary database at: {}'.format(self.dir_base))
            os.makedirs(self.dir_entries)


    def new_entry(self, date=None, device_name=DEVICE_NAME):
        if date is None: date = datetime.datetime.today()

        # This avoids the bug of not being able to create multiple entries in
        # the same second, a better approach would be to not have the date tied
        # to the ID so closely and allow multiple entries with the same date to
        # exist

        while True:
            timestamp = date.strftime('%s')
            month = date.strftime('%Y-%m')
            filename = 'diary-{}-{}.txt'.format(timestamp, device_name)
            entry = Entry(self.dir_entries, month, filename)

            if os.path.exists(entry._pathname):
                date += datetime.timedelta(seconds=1)
            else:
                break

        return entry


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
