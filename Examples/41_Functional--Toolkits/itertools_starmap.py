# itertools_starmap.py
from itertools import starmap

print(list(starmap(pow, [(2, 5), (3, 2)])))
#: [32, 9]
