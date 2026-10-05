# test_class_patterns.py
import pytest
from class_patterns import locate
from point import Point

@pytest.mark.parametrize("point, expected", [
    (Point(0, 0), "The origin"),
    (Point(0, 5), "On the y-axis at y=5"),
    (Point(3, 0), "On the x-axis at x=3"),
    (Point(3, 4), "At (3, 4)"),
])
def test_locate_matches_fields(point: Point,
                               expected: str) -> None:
    assert locate(point) == expected
