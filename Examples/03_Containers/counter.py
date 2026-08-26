# counter.py
from collections import Counter

words = "a cat sat on a mat a cat".split()
counts = Counter(words)
print(counts)
#: Counter({'a': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1})
print(counts["a"])
#: 3
print(counts["dog"])
#: 0
print("dog" in counts)  # Reading it added nothing
#: False
print(counts.most_common(2))
#: [('a', 3), ('cat', 2)]
