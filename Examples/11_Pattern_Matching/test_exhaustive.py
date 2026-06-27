# test_exhaustive.py
from exhaustive import Circle, Square, area

def test_exhaustive_area() -> None:
    assert round(area(Circle(1.0)), 4) == 3.1416
    assert area(Square(2.0)) == 4.0
