# test_class_patterns.py
from class_patterns import locate
from point import Point

def test_class_patterns() -> None:
    assert locate(Point(0, 0)) == "The origin"
    assert locate(Point(3, 0)) == "On the x-axis at x=3"
    assert locate(Point(3, 4)) == "At (3, 4)"
