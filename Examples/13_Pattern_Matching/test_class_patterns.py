# test_class_patterns.py
import pytest
from class_patterns import locate
from keyword_patterns import describe
from point import Point

@pytest.mark.parametrize("point, expected", [
    (Point(0, 0), "The origin"),
    (Point(3, 0), "On the x-axis at x=3"),
    (Point(3, 4), "At (3, 4)"),
])
def test_class_patterns(point: Point, expected: str) -> None:
    assert locate(point) == expected

@pytest.mark.parametrize("point, expected", [
    (Point(0, 5), "Somewhere on the y-axis"),
    (Point(3, 0), "Somewhere on the x-axis"),
    (Point(2, 2), "On the diagonal at 2"),
    (Point(3, 4), "Just some point"),
])
def test_keyword_patterns(point: Point, expected: str) -> None:
    assert describe(point) == expected
