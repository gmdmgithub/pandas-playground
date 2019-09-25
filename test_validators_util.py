import unittest

import validators_util as vu

class TestValidatorsUtil(unittest.TestCase):
    
    def test_validate_birthday(self):
        self.assertEqual(vu.validate_birthday('BE|00012511148|20000125'), True)
        self.assertEqual(vu.validate_birthday('BE|63052800924|19630528'), True)
        self.assertEqual(vu.validate_birthday('BE|10012511148|2000025'), False)
        self.assertEqual(vu.validate_birthday(2), False)
        self.assertEqual(vu.validate_birthday(True), False)
        self.assertEqual(vu.validate_birthday(None), False)