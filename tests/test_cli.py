import unittest
import re
import os.path
import shlex
from tempfile import TemporaryDirectory
from .filler_text import random_text
from diary.cli import process_args

class CLITestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.output_file_index = 0

    def tearDown(self):
        self.temp_dir.cleanup()

    def exec(self, string):
        args = ['-b', self.temp_dir.name]
        args.extend(shlex.split(string))
        process_args(args)

    def list_output(self, string=''):
        temp_text_file = os.path.join(self.temp_dir.name, 
                'temp{}.txt'.format(self.output_file_index))
        self.output_file_index += 1

        self.exec('list --pipe-to "cat > {}" {}'.format(temp_text_file, string))
        with open(temp_text_file) as f:
            text = f.read()
        return text

    def populate(self, num_entries=20):
        for i in range(num_entries):
            self.exec('new -m "{}"'.format(shlex.quote(random_text())))

    def test_list(self):
        self.populate(20)
        text = self.list_output()
        self.assertTrue(len(text.split('\n'))>20*3)

    def test_edit(self):
        self.exec('new --message "Hello world"')
        original_text = self.list_output()

        self.exec('edit -m "New text"')
        modified_text = self.list_output()

        self.assertTrue(re.search('Hello world', original_text))
        self.assertTrue(re.search('New text', modified_text))
        self.assertTrue(re.sub('Hello world', 'New text', original_text))

    def test_search(self):
        self.populate(2)
        search_string = 'stringthatwontgetgeneratedbyaccident'
        self.exec('new -m "hello world\n test text {}inthisentry"'.format(search_string))
        self.populate(2)
        all_entries = self.list_output()
        search_matches = self.list_output(search_string)

        self.assertNotEqual(all_entries, search_matches)
        self.assertTrue(re.search(search_string, all_entries))
        self.assertTrue(re.search(search_string, search_matches))
