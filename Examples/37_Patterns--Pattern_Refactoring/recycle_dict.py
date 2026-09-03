# recycle_dict.py
from collections import defaultdict
from parse_trash import parse
from trash import Bins, sum_value

bins: Bins = defaultdict(list)

for t in parse("trash.dat"):
    bins[type(t)].append(t)  # Bin chosen by the trash piece

for kind, items in bins.items():
    print(f"--- {kind.__name__} ---")
    sum_value(items)
#: --- Glass ---
#: Total value = 88.78
#: --- Paper ---
#: Total value = 21.20
#: --- Aluminum ---
#: Total value = 584.50
#: --- Cardboard ---
#: Total value = 120.08
