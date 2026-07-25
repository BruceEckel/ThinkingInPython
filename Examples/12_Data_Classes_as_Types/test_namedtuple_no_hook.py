# test_namedtuple_no_hook.py
from typing import NamedTuple
import pytest
from validation import TypeFailure, check

class Stars(NamedTuple):
    number: int

def make_stars(number: int) -> Stars:  # Validation lives outside
    check(1 <= number <= 10, f"Stars({number})")
    return Stars(number)

def test_the_factory_rejects_illegal_values() -> None:
    assert make_stars(10).number == 10
    with pytest.raises(TypeFailure):
        make_stars(11)

def test_the_type_accepts_them_anyway() -> None:
    assert Stars(11).number == 11  # Calling the type skips the check

def test_the_check_cannot_move_inside() -> None:
    with pytest.raises(AttributeError, match="Cannot overwrite"):
        class Validated(NamedTuple):
            number: int

            def __new__(cls, number: int) -> Validated:  # type: ignore
                check(1 <= number <= 10, f"Stars({number})")
                return tuple.__new__(cls, (number,))
