# messenger_idiom.py
from typing import Any


class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs


m: Any = Messenger(info="some information", b=['a', 'list'])
m.more = 11
print(m.info, m.b, m.more)
