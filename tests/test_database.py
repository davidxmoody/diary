import unittest
import random
from tempfile import TemporaryDirectory
from diary.server.database import connect
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
            entry.text = random_text()

    def test_empty_initially(self):
        num_entries = len(list(self.conn.get_entries()))
        self.assertEqual(num_entries, 0)

    def test_new_entry(self):
        entry = self.conn.new_entry()
        text = 'hello world'
        entry.text = text
        self.assertEqual(text, entry.text)

    def test_populate(self):
        self.populate(15)
        num_actual_entries = len(list(self.conn.get_entries()))
        self.assertEqual(15, num_actual_entries)

    def test_persistence(self):
        self.populate(15)
        texts = []
        for entry in self.conn.get_entries():
            texts.append(entry.text)

        self.conn = connect(self.temp_dir.name)
        new_texts = []
        for entry in self.conn.get_entries():
            new_texts.append(entry.text)

        self.assertEqual(texts, new_texts)
        self.assertEqual(len(texts), 15)

    def test_search(self):
        letters = 'abcdefghijklmnopqrstuvwxyz#'
        random_string = ''.join(random.choice(letters) for i in range(20))
        text = random_text() + random_string + random_text()

        self.populate()
        self.conn.new_entry().text = text
        search_results = list(self.conn.search_entries(random_string))

        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].text, text)

    def test_editing(self):
        entry = self.conn.new_entry()
        original_text = 'hello world'
        entry.text = original_text
        self.assertEqual(entry.text, original_text)

        entry.text = 'qwerty'
        self.assertNotEqual(original_text, entry.text)

    def test_wordcount(self):
        entry = self.conn.new_entry()
        entry.text = 'hello world'
        self.assertEqual(entry.wordcount, 2)

    def test_most_recent(self):
        self.populate()
        entry = self.conn.new_entry()
        entry.text = 'hello world'
        most_recent = self.conn.most_recent_entry()
        self.assertEqual(entry.id, most_recent.id)

    def test_find_by_id(self):
        self.populate(20)
        entry = list(self.conn.get_entries())[10]
        found_entry = self.conn.find_by_id(entry.id)
        self.assertEqual(entry.id, found_entry.id)
        self.assertEqual(entry.text, found_entry.text)

    def test_descending_get_entries(self):
        self.populate()
        ascending_entries = list(self.conn.get_entries(descending=False))
        descending_entries = list(self.conn.get_entries(descending=True))
        for entry1, entry2 in zip(ascending_entries, reversed(descending_entries)):
            self.assertEqual(entry1.id, entry2.id)
            self.assertEqual(entry1.text, entry2.text)
