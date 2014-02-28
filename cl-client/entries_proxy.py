class Entry():
    def __init__(self, json):
        pass

    @property
    def id(self):
        pass #TODO

    @property
    def date(self):
        pass #TODO

    @property
    def wordcount(self):
        pass #TODO

    @property
    def text(self):
        pass #TODO

    def command_line_edit(self):
        pass #TODO


class connect():
    def __init__(self, dir_base):
        pass #TODO maybe replace dir_base with a more general location such as a port number

    def new_entry(self, date=None, device_name='unknown'):
        pass #TODO return an entry with a command_line_edit() function 
             # or otherwise solve the problem in a different way

    def get_entries(self, descending=False, min_date=None, max_date=None):
        pass #TODO implement getting entries, maybe implement a generator with paging

    def search_entries(self, *search_terms, **kwargs):
        pass #TODO implement search

    def most_recent_entry(self):
        pass #TODO return most recent entry (entry with greatest date)

    def find_by_id(self, entry_id):
        pass #TODO return the entry with that id or None if not found
