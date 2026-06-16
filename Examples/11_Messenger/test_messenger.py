# test_messenger.py
from typing import Any

from messenger_idiom import Messenger
from messenger_modern import Color, Point


def test_messenger_exposes_kwargs_as_attributes() -> None:
    m: Any = Messenger(info="hi", count=3)
    assert m.info == "hi"
    assert m.count == 3
    m.added = 9  # attributes can be added afterward, too
    assert m.added == 9


def test_dataclass_point_has_fields_and_equality() -> None:
    assert Point(1.0, 2.0).x == 1.0
    assert Point(1.0, 2.0) == Point(1.0, 2.0)
    assert Point(1.0, 2.0) != Point(1.0, 3.0)


def test_namedtuple_color_is_a_named_record() -> None:
    c = Color(255, 0, 0)
    assert c.r == 255
    assert (c.r, c.g, c.b) == tuple(c)
