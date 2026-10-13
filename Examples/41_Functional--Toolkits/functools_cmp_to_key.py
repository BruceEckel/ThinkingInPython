# functools_cmp_to_key.py
from functools import cmp_to_key

def larger_first(a: str, b: str) -> int:
    return (b + a > a + b) - (b + a < a + b)

numbers = ["3", "30", "34", "5", "9"]
ordered = sorted(numbers, key=cmp_to_key(larger_first))
print("".join(ordered))
#: 9534330
