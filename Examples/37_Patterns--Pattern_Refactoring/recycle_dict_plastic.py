# recycle_dict_plastic.py
from typing import ClassVar
from dict_sorter import sort_by_type
from parse_trash import parse
from trash import Trash, report

class Plastic(Trash):
    value: ClassVar[float] = 0.15

pieces = parse("plastic.dat")
bins = sort_by_type(pieces)
report(bins)
#: Glass: 2.30
#: Plastic: 9.00
#: Aluminum: 50.10
binned = sum(len(v) for v in bins.values())
print(f"parsed {len(pieces)}, binned {binned}")
#: parsed 4, binned 4
