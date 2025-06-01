# test_functions.py

def square(x):
    return x * x

def is_even(n):
    return n % 2 == 0

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def count_characters(s):
    counts = {}
    for c in s:
        if c in counts:
            counts[c] += 1
        else:
            counts[c] = 1
    return counts

def reverse_words(sentence):
    return ' '.join(reversed(sentence.split()))

def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]

def unique_elements(seq):
    seen = set()
    output = []
    for item in seq:
        if item not in seen:
            output.append(item)
            seen.add(item)
    return output

def is_palindrome(word):
    cleaned = ''.join(c for c in word.lower() if c.isalnum())
    return cleaned == cleaned[::-1]

def merge_dicts(d1, d2):
    return {**d1, **d2}

def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

def transpose_matrix(matrix):
    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]

def rotate_left(lst, k):
    k %= len(lst)
    return lst[k:] + lst[:k]

def string_compression(s):
    if not s:
        return ''
    result = []
    count = 1
    prev = s[0]
    for char in s[1:]:
        if char == prev:
            count += 1
        else:
            result.append(prev + str(count))
            prev = char
            count = 1
    result.append(prev + str(count))
    return ''.join(result)

def longest_common_prefix(strings):
    if not strings:
        return ''
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ''
    return prefix

def powerset(seq):
    result = [[]]
    for elem in seq:
        result += [x + [elem] for x in result]
    return result

def memoized_fib(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = memoized_fib(n - 1, memo) + memoized_fib(n - 2, memo)
    return memo[n]

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insert = previous_row[j + 1] + 1
            delete = current_row[j] + 1
            substitute = previous_row[j] + (c1 != c2)
            current_row.append(min(insert, delete, substitute))
        previous_row = current_row

    return previous_row[-1]

def balanced_brackets(s):
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    for char in s:
        if char in pairs:
            stack.append(pairs[char])
        elif char in pairs.values():
            if not stack or stack.pop() != char:
                return False
    return not stack
