import unittest
import sys
import os
sys.path.append(os.path.dirname(__file__))

from basic_example_functions import add, subtract


class TestBasicExampleFunctions(unittest.TestCase):
    
    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)
        
    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -2), -3)
        
    def test_subtract_positive_numbers(self):
        self.assertEqual(subtract(5, 3), 2)


if __name__ == '__main__':
    unittest.main()