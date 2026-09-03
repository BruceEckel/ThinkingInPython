# recycle_rtti.py
from collections import defaultdict
from parse_trash import parse
from trash import (Aluminum, Bins, Cardboard, Glass,
                   Paper, sum_value)

bins: Bins = defaultdict(list)
for t in parse("trash.dat"):
    match t:
        case Aluminum():
            bins[Aluminum].append(t)
        case Paper():
            bins[Paper].append(t)
        case Glass():
            bins[Glass].append(t)
        case Cardboard():
            bins[Cardboard].append(t)
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
