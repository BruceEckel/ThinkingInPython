# test_exhaustive.py
import pytest
from exhaustive import Circle, Square, area

def test_exhaustive_area() -> None:
    assert round(area(Circle(1.0)), 4) == 3.1416
    assert area(Square(2.0)) == 4.0

def test_assert_never_rejects_a_lying_value() -> None:
    with pytest.raises(AssertionError):
        area("x")  # type: ignore
