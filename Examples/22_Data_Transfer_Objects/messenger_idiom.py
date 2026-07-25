# messenger_idiom.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="Spam", b=["x", "y"])
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y']}
m.more = 11
print(m.info, m.b, m.more)
#: Spam ['x', 'y'] 11
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11}
