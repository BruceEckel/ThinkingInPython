# defaultdict.py
from collections import defaultdict

pets = [("dog", "Rex"), ("cat", "Felix"), ("dog", "Fido")]
# With a plain dict you must create each list before appending:
plain = {}
for kind, name in pets:
    if kind not in plain:
        plain[kind] = []
    plain[kind].append(name)
print(plain["dog"])
#: ['Rex', 'Fido']
# A defaultdict creates the missing list for you:
by_kind = defaultdict(list)
for kind, name in pets:
    by_kind[kind].append(name)
print(by_kind["dog"])
#: ['Rex', 'Fido']
print(by_kind["fish"])  # A missing key gets a fresh empty list
#: []
