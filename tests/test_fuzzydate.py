import unittest
from diary.fuzzydate import custom_date

class CustomDateTestCase(unittest.TestCase):
    def test_custom_date(self):
        date = custom_date('2012-02-03')
        self.assertEqual(date.year, 2012)
        self.assertEqual(date.month, 2)
        self.assertEqual(date.day, 3)
