# test_encapsulation.py
import dataclasses

import pytest
from immutable import Bob, Immutable
from leaky import Leaky
from plugged import Plugged


def test_getter_leaks_internal_state() -> None:
    leaky = Leaky([1, 2])
    leaky.numbers.append(999)  # Reaches the real internal list.
    assert leaky.numbers == [1, 2, 999]


def test_defensive_copy_prevents_the_leak() -> None:
    plugged = Plugged([1, 2])
    plugged.numbers.append(999)  # Mutates only a copy.
    assert plugged.numbers == [1, 2]


def test_frozen_cannot_be_mutated() -> None:
    immutable = Immutable((1, 2), Bob())
    with pytest.raises(dataclasses.FrozenInstanceError):
        # Frozen, so the assignment fails:
        setattr(immutable.bob, "name", "Ralph")
