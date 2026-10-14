# recycle_rtti.py
from parse_trash import parse
from rtti_sorter import sort_by_match
from trash import report

report(sort_by_match(parse("trash.dat")))
#: Glass: 88.78
#: Paper: 21.20
#: Aluminum: 584.50
#: Cardboard: 120.08
