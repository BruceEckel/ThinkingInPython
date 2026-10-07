# singleton_class_demo.py
from singleton_class import Registry

first = Registry("primary", limit=3)
#: singleton.__call__(('primary',), {'limit': 3})
#: constructing Registry
#: Registry.__init__(primary, 3)
first.items.append("spam")
first.items.append("eggs")
second = Registry("secondary", limit=99)
#: singleton.__call__(('secondary',), {'limit': 99})
#: using cached Registry
#: discarding ('secondary',), {'limit': 99}
print(first is second, second.name,
      second.limit, second.items)
#: True primary 3 ['spam', 'eggs']
