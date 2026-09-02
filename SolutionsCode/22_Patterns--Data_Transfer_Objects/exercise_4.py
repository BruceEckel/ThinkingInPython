# exercise_4.py
from types import SimpleNamespace

TAGS = ["urgent", "todo"]

built = SimpleNamespace(
    info="Spam", tags=TAGS, more=11, note=12)
print(list(vars(built)))
#: ['info', 'tags', 'more', 'note']

assigned = SimpleNamespace(
    info="Spam", tags=TAGS, more=11)
assigned.note = 12
print(list(vars(assigned)))
#: ['info', 'tags', 'more', 'note']

print(vars(built) == vars(assigned))
#: True
