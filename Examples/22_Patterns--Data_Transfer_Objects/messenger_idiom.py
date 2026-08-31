# messenger_idiom.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="Spam", tags=["urgent", "todo"])
print(vars(m))
#: {'info': 'Spam', 'tags': ['urgent', 'todo']}
m.more = 11
print(m.info, m.tags, m.more)
#: Spam ['urgent', 'todo'] 11
print(vars(m))
#: {'info': 'Spam', 'tags': ['urgent', 'todo'], 'more': 11}
