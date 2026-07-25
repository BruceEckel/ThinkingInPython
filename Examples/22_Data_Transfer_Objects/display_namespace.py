# display_namespace.py
from types import SimpleNamespace

m = SimpleNamespace(info="Spam", b=["x", "y"])
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y']}
m.more = 11
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11}
