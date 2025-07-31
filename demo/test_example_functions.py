import unittest
import example_functions

class TestExampleFunctions(unittest.TestCase):
```python
import unittest

def add(a, b):
    return a + b

class TestAdd(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)
```
```python
import unittest

def subtract(a, b):
    return a - b

class TestSubtract(unittest.TestCase):
    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract(10, 5), 5)
        self.assertEqual(subtract(0, 0), 0)
        self.assertEqual(subtract(-5, 3), -8)
        self.assertEqual(subtract(5, -3), 8)

```


if __name__ == '__main__':
    unittest.main()