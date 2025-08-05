import unittest
import sys
import os
sys.path.append(os.path.dirname(__file__))

from medium_complexity import validate_user_data


class TestMediumComplexity(unittest.TestCase):
    
    def test_valid_user_data(self):
        """Test with valid user data."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 25
        }
        result = validate_user_data(user_data)
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])
    
    def test_missing_required_fields(self):
        """Test with missing required fields."""
        user_data = {"name": "John"}
        result = validate_user_data(user_data)
        self.assertFalse(result["valid"])
        self.assertIn("Missing required field: email", result["errors"])
        self.assertIn("Missing required field: age", result["errors"])
    
    def test_invalid_email(self):
        """Test with invalid email format."""
        user_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "age": 25
        }
        result = validate_user_data(user_data)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid email format", result["errors"])
    
    def test_negative_age(self):
        """Test with negative age."""
        user_data = {
            "name": "John Doe", 
            "email": "john@example.com",
            "age": -5
        }
        result = validate_user_data(user_data)
        self.assertFalse(result["valid"])
        self.assertIn("Age cannot be negative", result["errors"])


if __name__ == '__main__':
    unittest.main()