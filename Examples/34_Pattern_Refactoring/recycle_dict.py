# recycle_dict.py
from collections import defaultdict
from parse_trash import parse
from trash import Trash, sum_value

bins: dict[type[Trash], list[Trash]] = defaultdict(list)

for t in parse("trash.dat"):
    bins[type(t)].append(t)  # Bin chosen by the trash piece

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
