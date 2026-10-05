# test_immutable.py
import dataclasses
import pytest
from immutable import Bob, Immutable

def test_frozen_field_refuses_assignment() -> None:
    immutable = Immutable((1, 2), Bob())
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(immutable.bob, "name", "Ralph")
