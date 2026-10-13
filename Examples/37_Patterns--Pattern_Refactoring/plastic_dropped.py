# plastic_dropped.py
from collections import defaultdict
from typing import ClassVar
from parse_trash import parse
from trash import (Aluminum, Bins, Cardboard, Glass, Paper,
                   Trash, report)

class Plastic(Trash):
    value: ClassVar[float] = 0.15

pieces = parse("plastic.dat")
bins: Bins = defaultdict(list)
for piece in pieces:
    match piece:
        case Aluminum():
            bins[Aluminum].append(piece)
        case Paper():
            bins[Paper].append(piece)
        case Glass():
            bins[Glass].append(piece)
        case Cardboard():
            bins[Cardboard].append(piece)
report(bins)
#: Glass: 2.30
#: Aluminum: 50.10
binned = sum(len(v) for v in bins.values())
print(f"parsed {len(pieces)}, binned {binned}")
#: parsed 4, binned 2
