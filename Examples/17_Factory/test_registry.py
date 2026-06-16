# test_registry.py
import pytest
from registry import Circle, Shape, Square, make


def test_subclasses_auto_register() -> None:
    assert Shape.registry["Circle"] is Circle
    assert Shape.registry["Square"] is Square


def test_make_builds_the_right_type() -> None:
    assert isinstance(make("Circle"), Circle)
    assert isinstance(make("Square"), Square)


def test_new_subclass_registers_itself() -> None:
    class Triangle(Shape):
        def draw(self) -> None: ...

    assert Shape.registry["Triangle"] is Triangle
    assert isinstance(make("Triangle"), Triangle)


def test_unknown_name_raises() -> None:
    with pytest.raises(KeyError):
        make("Hexagon")
