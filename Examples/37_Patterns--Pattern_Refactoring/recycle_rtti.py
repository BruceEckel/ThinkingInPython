# recycle_rtti.py
from collections import defaultdict
from parse_trash import parse
from trash import (Aluminum, Bins, Cardboard, Glass,
                   Paper, report)

bins: Bins = defaultdict(list)
for piece in parse("trash.dat"):
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
#: Glass: 88.78
#: Paper: 21.20
#: Aluminum: 584.50
#: Cardboard: 120.08
