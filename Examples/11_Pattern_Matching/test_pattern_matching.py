# test_pattern_matching.py
from class_patterns import Point, locate
from exhaustive import Circle, Square, area
from mapping_patterns import handle
from sequence_patterns import summarize

def test_sequence_patterns() -> None:
    assert summarize([]) == "empty"
    assert summarize([5]) == "one item: 5"
    assert summarize([1, 2, 3]) == "1, then 2 more"

def test_class_patterns() -> None:
    assert locate(Point(0, 0)) == "the origin"
    assert locate(Point(3, 0)) == "on the x-axis at x=3"
    assert locate(Point(3, 4)) == "at (3, 4)"

def test_mapping_patterns() -> None:
    assert handle({"type": "key", "key": "Esc"}) == "key Esc"
    assert handle({"nope": 1}) == "not an event"

def test_exhaustive_area() -> None:
    assert round(area(Circle(1.0)), 4) == 3.1416
    assert area(Square(2.0)) == 4.0
