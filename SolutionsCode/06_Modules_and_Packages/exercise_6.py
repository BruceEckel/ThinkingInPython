# exercise_6.py
from exporting_no_all import *  # noqa: F403

print(sorted(n for n in dir() if not n.startswith("__")))
#: ['helper', 'public', 'undeclared']
