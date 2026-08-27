# display_namespace.py
from types import SimpleNamespace

m = SimpleNamespace(info="Spam", tags=["urgent", "todo"])
print(vars(m))
#: {'info': 'Spam', 'tags': ['urgent', 'todo']}
m.more = 11
print(m)
#: namespace(info='Spam', tags=['urgent', 'todo'], more=11)
print(m == SimpleNamespace(info="Spam",
                           tags=["urgent", "todo"],
                           more=11))
#: True
