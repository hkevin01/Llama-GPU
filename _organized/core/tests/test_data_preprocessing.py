import unittest
from src.utils.data_preprocessing import clean_text, to_lower, preprocess_input

class TestDataPreprocessing(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(clean_text('Hello! 123.'), 'Hello 123')
    def test_to_lower(self):
        self.assertEqual(to_lower('ABC'), 'abc')
    def test_preprocess_input(self):
        self.assertEqual(preprocess_input('  HeLLo! 123.  '), 'hello 123')

if __name__ == '__main__':
    unittest.main()
