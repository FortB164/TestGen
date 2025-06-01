# string_utils.py

import re
from collections import Counter
from typing import Optional, Callable


def reverse_string(s: str) -> str:
    return s[::-1]

def is_palindrome(s: str) -> bool:
    s_clean = re.sub(r'[^a-z0-9]', '', s.lower())
    return s_clean == s_clean[::-1]

def count_vowels(s: str) -> int:
    return sum(c in 'aeiou' for c in s.lower())

def title_case(s: str) -> str:
    return s.title()

def remove_duplicate_words(s: str) -> str:
    seen = set()
    words = []
    for word in s.split():
        if word not in seen:
            seen.add(word)
            words.append(word)
    return ' '.join(words)

def char_frequency(s: str) -> dict:
    return dict(Counter(s))

def normalize_whitespace(s: str) -> str:
    return ' '.join(s.split())

def smart_truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len].rsplit(' ', 1)[0] + '...'

def transform_string(s: str, func: Callable[[str], str]) -> str:
    """Applies a function to each word in the string."""
    return ' '.join(func(word) for word in s.split())
