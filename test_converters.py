import unittest

import converters as cnv

class TestConverters(unittest.TestCase):

    def test_pep(self):
        self.assertEqual(cnv.pep('Y'), True)
        self.assertEqual(cnv.pep(23), False)
        self.assertEqual(cnv.pep(True), False)
    
    def test_street_converter(self):
        self.assertEqual(cnv.street_converter('ABC BC CD'),('ABC BC CD', None, None))
        self.assertEqual(cnv.street_converter(' ABC'),('ABC', None, None))
        self.assertEqual(cnv.street_converter('ABC  23B'),('ABC', '23B', None))
        self.assertEqual(cnv.street_converter('ABC BCD 23B/ A3'),('ABC BCD', '23B', 'A3'))
        self.assertEqual(cnv.street_converter('ABC LE 205     RUE BESTE 205/1.3'),('ABC LE 205 RUE BESTE', '205', '1.3'))
        self.assertEqual(cnv.street_converter('AVENUE DES MMMSSSCCC 57BTE23'),('AVENUE DES MMMSSSCCC', '57', '23'))