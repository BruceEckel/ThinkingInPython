# messenger_idiom.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="Some information", b=["a", "list"])
m.more = 11
print(m.info, m.b, m.more)
#: Some information ['a', 'list'] 11
print(vars(m))
#: {'info': 'Some information', 'b': ['a', 'list'], 'more': 11}
