# functools_cmp_to_key.py
from functools import cmp_to_key

def by_length_desc(a: str, b: str) -> int:
    return len(b) - len(a)

words = ["a", "ccc", "bb"]
print(sorted(words, key=cmp_to_key(by_length_desc)))
#: ['ccc', 'bb', 'a']
