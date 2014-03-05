import unittest
import random
from tempfile import TemporaryDirectory
from server.database import connect
from .filler_text import random_text

class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.conn = connect(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def populate(self, num_entries=20):
        for i in range(num_entries):
            entry = self.conn.new_entry()
            text = random_text()
            #TODO change the way new entries have their text edited
            entry.command_line_edit('echo -n "{}" >'.format(text))

    def test_new_entry(self):
        entry = self.conn.new_entry()
        text = 'hello world'
        entry.command_line_edit('echo -n "{}" >'.format(text))
        self.assertEqual(text, entry.text)

    def test_empty_initially(self):
        num_entries = len(list(self.conn.get_entries()))
        self.assertEqual(num_entries, 0)

    def test_populate(self):
        self.populate(20)
        num_actual_entries = len(list(self.conn.get_entries()))
        self.assertEqual(20, num_actual_entries)

    def test_persistence(self):
        self.populate(20)
        texts = []
        for entry in self.conn.get_entries():
            texts.append(entry.text)

        self.conn = connect(self.temp_dir.name)
        num_actual_entries = len(list(self.conn.get_entries()))
        self.assertEqual(20, num_actual_entries)
        new_texts = []
        for entry in self.conn.get_entries():
            new_texts.append(entry.text)
        self.assertEqual(texts, new_texts)

    def test_search(self):
        letters = 'abcdefghijklmnopqrstuvwxyz#'
        random_string = ''.join(random.choice(letters) for i in range(20))
        text = random_text() + random_string + random_text()
        self.populate()
        self.conn.new_entry().command_line_edit('echo -n "{}" >'.format(text))
        search_result = list(self.conn.search_entries(random_string))[0]
        self.assertEqual(search_result.text, text)
