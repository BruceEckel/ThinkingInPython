# recycle_dict_plastic.py
from collections import defaultdict
from typing import ClassVar
from parse_trash import parse
from trash import Bins, Trash, report

class Plastic(Trash):
    value: ClassVar[float] = 0.15

pieces = parse("plastic.dat")
bins: Bins = defaultdict(list)
for piece in pieces:
    bins[type(piece)].append(piece)  # Piece picks its bin
report(bins)
#: Glass: 2.30
#: Plastic: 9.00
#: Aluminum: 50.10
binned = sum(len(v) for v in bins.values())
print(f"parsed {len(pieces)}, binned {binned}")
#: parsed 4, binned 4
