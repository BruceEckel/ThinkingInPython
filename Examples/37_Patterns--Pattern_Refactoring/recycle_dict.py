# recycle_dict.py
from collections import defaultdict
from parse_trash import parse
from trash import Bins, report

bins: Bins = defaultdict(list)
for piece in parse("trash.dat"):
    bins[type(piece)].append(piece)  # Piece picks its bin
report(bins)
#: Glass: 88.78
#: Paper: 21.20
#: Aluminum: 584.50
#: Cardboard: 120.08
