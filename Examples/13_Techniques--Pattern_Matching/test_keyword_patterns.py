# test_keyword_patterns.py
import pytest
from keyword_patterns import describe
from point import Point

@pytest.mark.parametrize("point, expected", [
    (Point(0, 5), "Somewhere on the y-axis"),
    (Point(3, 0), "Somewhere on the x-axis"),
    (Point(3, 4), "Just some point"),
])
def test_keyword_patterns(point: Point,
                          expected: str) -> None:
    assert describe(point) == expected
