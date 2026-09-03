# recycle_dict_plastic.py
from collections import defaultdict
from parse_trash import parse
from trash import Bins, Trash, sum_value

class Plastic(Trash):
    value = 0.15

pieces = parse("plastic.dat")
bins: Bins = defaultdict(list)
for t in pieces:
    bins[type(t)].append(t)  # Bin chosen by the trash piece

for kind, items in bins.items():
    print(f"--- {kind.__name__} ---")
    sum_value(items)
binned = sum(len(v) for v in bins.values())
print(f"parsed {len(pieces)}, binned {binned}")
#: --- Glass ---
#: Total value = 2.30
#: --- Plastic ---
#: Total value = 9.00
#: --- Aluminum ---
#: Total value = 50.10
#: parsed 4, binned 4
