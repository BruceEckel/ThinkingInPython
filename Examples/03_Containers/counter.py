# counter.py
from collections import Counter

words = "the cat sat on the mat the cat".split()
counts = Counter(words)
print(counts)
#: Counter({'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1})
print(counts["the"])
#: 3
print(counts["dog"])  # A missing key counts as zero
#: 0
print(counts.most_common(2))  # The two highest counts
#: [('the', 3), ('cat', 2)]
