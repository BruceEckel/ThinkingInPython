# plastic_dropped.py
from collections import defaultdict
from parse_trash import parse
from trash import (
    Aluminum,
    Bins,
    Cardboard,
    Glass,
    Paper,
    Trash,
    sum_value,
)

class Plastic(Trash):
    value = 0.15

pieces = parse("plastic.dat")
bins: Bins = defaultdict(list)
for t in pieces:
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
binned = sum(len(v) for v in bins.values())
print(f"parsed {len(pieces)}, binned {binned}")
#: --- Glass ---
#: weight of Glass = 10.0
#: Total value = 2.30
#: --- Aluminum ---
#: weight of Aluminum = 30.0
#: Total value = 50.10
#: parsed 4, binned 2
