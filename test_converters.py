import unittest

import converters as cnv

class TestConverters(unittest.TestCase):

    def test_pep(self):
        self.assertEqual(cnv.pep('Y'), True)
        self.assertEqual(cnv.pep(23), False)
        self.assertEqual(cnv.pep(True), False)