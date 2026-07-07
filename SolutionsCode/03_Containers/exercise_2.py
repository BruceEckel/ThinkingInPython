# exercise_2.py
from collections import defaultdict

pets = [("dog", "Rex"), ("cat", "Felix"), ("dog", "Fido")]
counts = defaultdict(int)
for kind, name in pets:
    counts[kind] += 1
print(dict(counts))
#: {'dog': 2, 'cat': 1}
