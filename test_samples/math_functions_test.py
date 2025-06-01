# math_functions_test.py

import unittest
import math
from math_functions import *

class TestMathFunctions(unittest.TestCase):
    # --- ADD ---
    def test_add_basic_1(self):
        """Test basic addition with positive numbers"""
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(10, 20), 30)
        self.assertEqual(add(0, 0), 0)

    def test_add_basic_2(self):
        """Test addition with negative numbers and floats"""
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(-5, -3), -8)
        self.assertAlmostEqual(add(0.1, 0.2), 0.3, places=7)

    def test_add_edge_1(self):
        """Test addition with large numbers"""
        self.assertEqual(add(1e10, 1e10), 2e10)
        self.assertEqual(add(float('inf'), 1), float('inf'))

    def test_add_edge_2(self):
        """Test addition with very small numbers"""
        self.assertAlmostEqual(add(1e-10, 1e-10), 2e-10)
        self.assertEqual(add(-0.0, 0.0), 0.0)

    def test_add_error_1(self):
        """Test addition with invalid types"""
        with self.assertRaises(TypeError):
            add("2", 3)
        with self.assertRaises(TypeError):
            add(None, 5)

    def test_add_error_2(self):
        """Test addition with complex numbers"""
        with self.assertRaises(TypeError):
            add(1+2j, 3+4j)

    # --- DIVIDE ---
    def test_divide_basic_1(self):
        """Test basic division"""
        self.assertEqual(divide(6, 2), 3)
        self.assertEqual(divide(10, 2), 5)
        self.assertEqual(divide(0, 5), 0)

    def test_divide_basic_2(self):
        """Test division with negative numbers"""
        self.assertEqual(divide(-6, 2), -3)
        self.assertEqual(divide(6, -2), -3)
        self.assertEqual(divide(-6, -2), 3)

    def test_divide_edge_1(self):
        """Test division with edge cases"""
        self.assertEqual(divide(float('inf'), 2), float('inf'))
        self.assertAlmostEqual(divide(1, 3), 1/3)

    def test_divide_edge_2(self):
        """Test division with very small numbers"""
        self.assertAlmostEqual(divide(1e-10, 2), 5e-11)
        self.assertAlmostEqual(divide(0.0001, 2), 0.00005)

    def test_divide_error_1(self):
        """Test division by zero"""
        with self.assertRaises(MathError):
            divide(5, 0)
        with self.assertRaises(MathError):
            divide(0, 0)

    def test_divide_error_2(self):
        """Test division with invalid types"""
        with self.assertRaises(TypeError):
            divide("6", 2)
        with self.assertRaises(TypeError):
            divide(6, "2")

    # --- FIBONACCI ---
    def test_fibonacci_basic_1(self):
        """Test basic Fibonacci numbers"""
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)
        self.assertEqual(fibonacci(2), 1)
        self.assertEqual(fibonacci(3), 2)

    def test_fibonacci_basic_2(self):
        """Test larger Fibonacci numbers"""
        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(fibonacci(20), 6765)

    def test_fibonacci_edge_1(self):
        """Test Fibonacci with edge cases"""
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_fibonacci_edge_2(self):
        """Test Fibonacci with larger numbers"""
        self.assertEqual(fibonacci(30), 832040)

    def test_fibonacci_error_1(self):
        """Test Fibonacci with negative numbers"""
        with self.assertRaises(MathError):
            fibonacci(-1)
        with self.assertRaises(MathError):
            fibonacci(-10)

    def test_fibonacci_error_2(self):
        """Test Fibonacci with invalid types"""
        with self.assertRaises(TypeError):
            fibonacci("5")
        with self.assertRaises(TypeError):
            fibonacci(None)

    def test_stats(self):
        data = [1, 2, 3, 4]
        self.assertAlmostEqual(mean(data), 2.5)
        self.assertAlmostEqual(stddev(data), 1.118, places=3)
        self.assertEqual(product(data), 24)

    def test_derivative_integral(self):
        f = lambda x: x**2
        df = derivative(f)
        self.assertAlmostEqual(df(2), 4.0, delta=0.01)
        area = integral(lambda x: 1, 0, 5)
        self.assertAlmostEqual(area, 5.0, delta=0.01)


if __name__ == "__main__":
    unittest.main()
