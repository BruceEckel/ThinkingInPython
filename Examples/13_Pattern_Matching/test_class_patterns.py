# test_class_patterns.py
from class_patterns import locate
from keyword_patterns import describe
from point import Point

def test_class_patterns() -> None:
    assert locate(Point(0, 0)) == "The origin"
    assert locate(Point(3, 0)) == "On the x-axis at x=3"
    assert locate(Point(3, 4)) == "At (3, 4)"

def test_keyword_patterns() -> None:
    assert describe(Point(0, 5)) == "Somewhere on the y-axis"
    assert describe(Point(3, 0)) == "Somewhere on the x-axis"
    assert describe(Point(2, 2)) == "On the diagonal at 2"
    assert describe(Point(3, 4)) == "Just some point"
