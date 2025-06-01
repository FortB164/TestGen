# string_utils_test.py

import unittest
from string_utils import *

class TestStringUtils(unittest.TestCase):
    # --- REVERSE STRING ---
    def test_reverse_string_basic_1(self):
        """Test basic string reversal"""
        self.assertEqual(reverse_string("hello"), "olleh")
        self.assertEqual(reverse_string("world"), "dlrow")

    def test_reverse_string_basic_2(self):
        """Test string reversal with spaces and special characters"""
        self.assertEqual(reverse_string("hello world!"), "!dlrow olleh")
        self.assertEqual(reverse_string("123!@#"), "#@!321")

    def test_reverse_string_edge_1(self):
        """Test string reversal with edge cases"""
        self.assertEqual(reverse_string(""), "")
        self.assertEqual(reverse_string("a"), "a")
        self.assertEqual(reverse_string("  "), "  ")

    def test_reverse_string_edge_2(self):
        """Test string reversal with unicode characters"""
        self.assertEqual(reverse_string("café"), "éfac")
        self.assertEqual(reverse_string("👋🌍"), "🌍👋")

    def test_reverse_string_error_1(self):
        """Test string reversal with invalid inputs"""
        with self.assertRaises(TypeError):
            reverse_string(None)
        with self.assertRaises(TypeError):
            reverse_string(123)

    def test_reverse_string_error_2(self):
        """Test string reversal with invalid types"""
        with self.assertRaises(TypeError):
            reverse_string([])
        with self.assertRaises(TypeError):
            reverse_string({})

    # --- IS PALINDROME ---
    def test_is_palindrome_basic_1(self):
        """Test basic palindrome detection"""
        self.assertTrue(is_palindrome("madam"))
        self.assertTrue(is_palindrome("A man, a plan, a canal, Panama"))

    def test_is_palindrome_basic_2(self):
        """Test non-palindrome strings"""
        self.assertFalse(is_palindrome("hello"))
        self.assertFalse(is_palindrome("world"))

    def test_is_palindrome_edge_1(self):
        """Test palindrome with empty and single character"""
        self.assertTrue(is_palindrome(""))
        self.assertTrue(is_palindrome("a"))

    def test_is_palindrome_edge_2(self):
        """Test palindrome with numbers and special chars"""
        self.assertTrue(is_palindrome("12321"))
        self.assertFalse(is_palindrome("12345"))

    def test_is_palindrome_error_1(self):
        """Test palindrome with invalid input"""
        with self.assertRaises(TypeError):
            is_palindrome(None)
        with self.assertRaises(TypeError):
            is_palindrome(123)

    def test_is_palindrome_error_2(self):
        """Test palindrome with invalid types"""
        with self.assertRaises(TypeError):
            is_palindrome([])
        with self.assertRaises(TypeError):
            is_palindrome({})

if __name__ == "__main__":
    unittest.main()
