# math_functions.py

import math
from functools import lru_cache, reduce
from typing import Callable, List, TypeVar, Optional

T = TypeVar('T', int, float)

class MathError(Exception):
    pass

def add(x: T, y: T) -> T:
    return x + y

def subtract(x: T, y: T) -> T:
    return x - y

def multiply(x: T, y: T) -> T:
    return x * y

def divide(x: T, y: T) -> T:
    if y == 0:
        raise MathError("Division by zero.")
    return x / y

def mean(values: List[T]) -> float:
    if not values:
        raise MathError("Mean of empty list.")
    return sum(values) / len(values)

def product(values: List[T]) -> T:
    return reduce(lambda x, y: x * y, values, 1)

def stddev(values: List[T]) -> float:
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / len(values))

@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    if n < 0:
        raise MathError("Negative index in Fibonacci.")
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def derivative(f: Callable[[float], float], dx: float = 1e-6) -> Callable[[float], float]:
    """Returns a numerical derivative function of f."""
    def df(x: float) -> float:
        return (f(x + dx) - f(x - dx)) / (2 * dx)
    return df

def integral(f: Callable[[float], float], a: float, b: float, steps: int = 1000) -> float:
    """Approximates the integral of f from a to b using the trapezoidal rule."""
    dx = (b - a) / steps
    total = 0.5 * (f(a) + f(b))
    for i in range(1, steps):
        total += f(a + i * dx)
    return total * dx
