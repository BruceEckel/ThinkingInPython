# test_point_distance.py
from point_distance import Point, distance

def test_method_and_function_agree() -> None:
    p1, p2 = Point(3, 0), Point(0, 4)
    assert p1.distance_to(p2) == 5
    assert distance(p1, p2) == 5
