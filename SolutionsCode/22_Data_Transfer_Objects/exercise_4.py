# exercise_4.py
from types import SimpleNamespace

built = SimpleNamespace(info="Spam", b=["x", "y"], more=11,
                        tag=12)
print(vars(built))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11, 'tag': 12}

assigned = SimpleNamespace(info="Spam", b=["x", "y"],
                           more=11)
assigned.tag = 12
print(vars(assigned))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11, 'tag': 12}

print(vars(built) == vars(assigned))
#: True
