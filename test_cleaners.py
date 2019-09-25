import unittest

import cleaners as cln

class TestCleaners(unittest.TestCase):
    def test_phone_prefix_updater(self):
        self.assertEqual(cln.phone_prefix_updater('UZ99890929921'),'99890929921')