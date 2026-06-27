# test_messenger_idiom.py
from typing import Any
from messenger_idiom import Messenger

def test_messenger_exposes_kwargs_as_attributes() -> None:
    m: Any = Messenger(info="hi", count=3)
    assert m.info == "hi"
    assert m.count == 3
    m.added = 9  # Attributes can be added afterward, too
    assert m.added == 9
