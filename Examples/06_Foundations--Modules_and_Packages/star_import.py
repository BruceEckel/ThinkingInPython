# star_import.py
from exporting import *  # noqa: F403

print(sorted(n for n in dir() if not n.startswith("__")))
#: ['helper', 'public']
