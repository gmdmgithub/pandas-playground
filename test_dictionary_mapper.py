import unittest

import dictionary_mapper as dm

class TestDictMapper(unittest.TestCase):
    
    #TODO!!! - review when known
    def test_segment_id(self):
        self.assertEqual(dm.segment_id(False),None)
        self.assertEqual(dm.segment_id(9999),None)
        self.assertEqual(dm.segment_id('9999'),'PERSONAL')
    
    def test_title(self):
        self.assertEqual(dm.title('Mme'),'AAA')
        self.assertEqual(dm.title('Mme'),'AAA')


    