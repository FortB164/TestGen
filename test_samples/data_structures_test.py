# data_structures_test.py

import unittest
from data_structures import *

class TestDataStructures(unittest.TestCase):
    # --- DEDUPLICATE LIST ---
    def test_deduplicate_list_basic_1(self):
        """Test basic list deduplication"""
        self.assertEqual(deduplicate_list([1, 2, 2, 3]), [1, 2, 3])
        self.assertEqual(deduplicate_list(['a', 'b', 'a']), ['a', 'b'])

    def test_deduplicate_list_basic_2(self):
        """Test deduplication with different types"""
        self.assertEqual(deduplicate_list([1, '1', 1.0]), [1, '1', 1.0])
        self.assertEqual(deduplicate_list([True, 1, True]), [True, 1])

    def test_deduplicate_list_edge_1(self):
        """Test deduplication with edge cases"""
        self.assertEqual(deduplicate_list([]), [])
        self.assertEqual(deduplicate_list([1]), [1])
        self.assertEqual(deduplicate_list([1, 1, 1]), [1])

    def test_deduplicate_list_edge_2(self):
        """Test deduplication with complex objects"""
        obj1 = {'a': 1}
        obj2 = {'a': 1}
        self.assertEqual(deduplicate_list([obj1, obj2]), [obj1, obj2])

    def test_deduplicate_list_error_1(self):
        """Test deduplication with invalid inputs"""
        with self.assertRaises(TypeError):
            deduplicate_list(None)
        with self.assertRaises(TypeError):
            deduplicate_list("not a list")

    def test_deduplicate_list_error_2(self):
        """Test deduplication with unhashable types"""
        with self.assertRaises(TypeError):
            deduplicate_list([[1], [1]])

    # --- MERGE DICTS ---
    def test_merge_dicts_basic_1(self):
        """Test merging two dicts with unique keys"""
        self.assertEqual(merge_dicts({"a": 1}, {"b": 2}), {"a": 1, "b": 2})

    def test_merge_dicts_basic_2(self):
        """Test merging with overlapping keys (should overwrite)"""
        self.assertEqual(merge_dicts({"a": 1}, {"a": 2}), {"a": 2})

    # --- INVERT DICT ---
    def test_invert_dict_basic_1(self):
        """Test inverting a simple dict"""
        self.assertEqual(invert_dict({"a": 1, "b": 2}), {1: "a", 2: "b"})

    def test_invert_dict_error_1(self):
        """Test inverting a dict with duplicate values"""
        with self.assertRaises(ValueError):
            invert_dict({"x": 1, "y": 1})

    # --- GROUP BY KEY ---
    def test_group_by_key_basic_1(self):
        """Test grouping by key"""
        people = [
            {"name": "Alice", "city": "NY"},
            {"name": "Bob", "city": "SF"},
            {"name": "Carol", "city": "NY"},
        ]
        grouped = group_by_key(people, "city")
        self.assertEqual(len(grouped["NY"]), 2)
        self.assertEqual(len(grouped["SF"]), 1)

    # --- NESTED GET ---
    def test_nested_get_basic_1(self):
        """Test nested get with valid keys"""
        d = {"a": {"b": {"c": 42}}}
        self.assertEqual(nested_get(d, ["a", "b", "c"]), 42)

    def test_nested_get_edge_1(self):
        """Test nested get with missing keys and default"""
        d = {"a": {"b": {"c": 42}}}
        self.assertEqual(nested_get(d, ["a", "x", "c"], default="fail"), "fail")

if __name__ == "__main__":
    unittest.main()
