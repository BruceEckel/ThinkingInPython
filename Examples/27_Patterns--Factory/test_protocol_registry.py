# test_protocol_registry.py
import pytest
from shape_registry import ShapeFactory

class Triangle:
    def draw(self) -> None: ...

def test_register_returns_the_class() -> None:
    make = ShapeFactory()
    assert make.register(Triangle) is Triangle
    assert make.registry == {"Triangle": Triangle}

def test_make_builds_a_registered_class() -> None:
    make = ShapeFactory()
    make.register(Triangle)
    assert isinstance(make("Triangle"), Triangle)

def test_each_factory_starts_empty() -> None:
    make = ShapeFactory()
    with pytest.raises(KeyError):
        make("Triangle")
