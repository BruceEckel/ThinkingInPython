# plastic_dropped.py
from typing import ClassVar
from parse_trash import parse
from rtti_sorter import sort_by_match
from trash import Trash, report

class Plastic(Trash):
    value: ClassVar[float] = 0.15

pieces = parse("plastic.dat")
bins = sort_by_match(pieces)
report(bins)
#: Glass: 2.30
#: Aluminum: 50.10
binned = sum(len(v) for v in bins.values())
print(f"parsed {len(pieces)}, binned {binned}")
#: parsed 4, binned 2
