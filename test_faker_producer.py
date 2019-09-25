import unittest

import faker_producer as fp

class TestFakerProducer(unittest.TestCase):
    
    def test_first_name(self):
        self.assertIsNone(fp.first_name(None))
        self.assertIsNotNone(fp.first_name('Alex'))
        