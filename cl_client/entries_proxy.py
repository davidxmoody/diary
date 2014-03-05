import requests  # Requires the requests module to be installed
from fuzzydate import custom_date  #TODO parse the date in a better way

class Entry():
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        self.date = custom_date(self.date)

    def command_line_edit(self):
        raise Exception('cannot edit entry: {}'.format(self.id))


class connect():
    def __init__(self, location):
        location = location[:-1] if location[-1]=='/' else location
        self.entries_url = '{}/entries'.format(location)

    def new_entry(self, date=None, device_name='unknown'):
        pass #TODO return an entry with a command_line_edit() function 
             # or otherwise solve the problem in a different way

    def get_entries(self, search_terms=None, descending=False, min_date=None, max_date=None):
        #TODO maybe implement a generator with paging
        params = {}
        params['order'] = 'desc' if descending else 'asc'
        if search_terms is not None and len(search_terms)>0:
            #TODO only the first search term is used, correct that
            params['q'] = search_terms[0]
        if min_date is not None:
            params['after'] = min_date
        if max_date is not None:
            params['before'] = max_date
        r = requests.get(self.entries_url, params=params)
        return [Entry(json_entry) for json_entry in r.json()]

    def most_recent_entry(self):
        r = requests.get(self.entries_url, params={'limit': 1, 'order': 'desc'})
        return Entry(r.json()[0])

    def find_by_id(self, entry_id):
        r = requests.get('{}/{}'.format(self.entries_url, entry_id))
        return Entry(r.json())
