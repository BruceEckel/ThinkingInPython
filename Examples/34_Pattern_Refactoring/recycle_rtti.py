# recycle_rtti.py
# First cut: sort by testing each type. It works, but it checks for
# EVERY type. Add a new kind of Trash and you must find and edit
# this code, with no help from the tools if you miss a spot. That is
# the smell to watch for.
from collections import defaultdict
from parse_trash import parse
from trash import Aluminum, Cardboard, Glass, Paper, Trash, sum_value

bins: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in parse("trash.dat"):
    if isinstance(t, Aluminum):
        bins[Aluminum].append(t)
    elif isinstance(t, Paper):
        bins[Paper].append(t)
    elif isinstance(t, Glass):
        bins[Glass].append(t)
    elif isinstance(t, Cardboard):
        bins[Cardboard].append(t)
for kind, items in bins.items():
    print(f"--- {kind.__name__} ---")
    sum_value(items)
#: --- Glass ---
#: weight of Glass = 54.0
#: weight of Glass = 17.0
#: weight of Glass = 11.0
#: weight of Glass = 68.0
#: weight of Glass = 43.0
#: weight of Glass = 63.0
#: weight of Glass = 50.0
#: weight of Glass = 80.0
#: Total value = 88.78
#: --- Paper ---
#: weight of Paper = 22.0
#: weight of Paper = 11.0
#: weight of Paper = 88.0
#: weight of Paper = 91.0
#: Total value = 21.20
#: --- Aluminum ---
#: weight of Aluminum = 89.0
#: weight of Aluminum = 76.0
#: weight of Aluminum = 25.0
#: weight of Aluminum = 34.0
#: weight of Aluminum = 27.0
#: weight of Aluminum = 18.0
#: weight of Aluminum = 81.0
#: Total value = 584.50
#: --- Cardboard ---
#: weight of Cardboard = 96.0
#: weight of Cardboard = 44.0
#: weight of Cardboard = 12.0
#: Total value = 120.08
