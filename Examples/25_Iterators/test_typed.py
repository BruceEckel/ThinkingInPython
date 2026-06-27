# test_typed.py
import pytest
from typed_generator import typed
from typed_iterator import TypedIterator

def test_typed_generator_passes_and_rejects() -> None:
    assert list(typed([1, 2, 3], int)) == [1, 2, 3]
    with pytest.raises(TypeError):
        list(typed([1, "two", 3], int))

def test_typed_iterator_passes_and_rejects() -> None:
    assert list(TypedIterator(iter([1, 2, 3]), int)) == [1, 2, 3]
    with pytest.raises(TypeError):
        list(TypedIterator(iter([1, "two"]), int))
