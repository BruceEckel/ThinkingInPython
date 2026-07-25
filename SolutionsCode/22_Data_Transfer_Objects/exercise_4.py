# exercise_4.py
from types import SimpleNamespace

built = SimpleNamespace(info="Spam", b=["x", "y"], more=11,
                        extra="eggs")
print(vars(built))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11, 'extra': 'eggs'}

assigned = SimpleNamespace(info="Spam", b=["x", "y"], more=11)
assigned.extra = "eggs"
print(vars(assigned))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11, 'extra': 'eggs'}

print(vars(built) == vars(assigned))
#: True
