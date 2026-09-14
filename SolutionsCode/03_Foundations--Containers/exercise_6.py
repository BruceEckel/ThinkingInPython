# exercise_6.py
from collections import defaultdict

words = "a cat sat on a mat a cat".split()
counts: defaultdict[str, int] = defaultdict(int)
for word in words:
    counts[word] += 1
print(dict(counts))
#: {'a': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1}
print(counts["dog"])  # Missing keys still read as zero
#: 0
print(sorted(counts.items(), key=lambda kv: -kv[1])[:2])
#: [('a', 3), ('cat', 2)]
