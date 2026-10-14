# recycle_dict.py
from dict_sorter import sort_by_type
from parse_trash import parse
from trash import report

report(sort_by_type(parse("trash.dat")))
#: Glass: 88.78
#: Paper: 21.20
#: Aluminum: 584.50
#: Cardboard: 120.08
