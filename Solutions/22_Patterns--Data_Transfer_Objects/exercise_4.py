# exercise_4.py
from types import SimpleNamespace
from typing import Final

TAGS: Final[list[str]] = ["urgent", "todo"]

built = SimpleNamespace(info="Spam", tags=TAGS, note=12)
built.more = 11
print(list(vars(built)))
#: ['info', 'tags', 'note', 'more']

assigned = SimpleNamespace(info="Spam", tags=TAGS)
assigned.more = 11
assigned.note = 12
print(list(vars(assigned)))
#: ['info', 'tags', 'more', 'note']

print(vars(built) == vars(assigned), built == assigned)
#: True True
