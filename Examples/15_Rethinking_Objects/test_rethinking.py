# test_rethinking.py
import distance_protocol as dp
import shapes_match as sm
import shapes_oo as so
from point_distance import Point, distance


def test_method_and_function_agree() -> None:
    p1, p2 = Point(3, 0), Point(0, 4)
    assert p1.distance_to(p2) == 5
    assert distance(p1, p2) == 5


def test_protocol_and_adapter() -> None:
    assert dp.distance(dp.Point(3, 0), dp.Point(0, 4)) == 5
    assert dp.distance(dp.PairCoord(dp.Pair(3, 0)),
                       dp.PairCoord(dp.Pair(0, 4))) == 5


def test_oo_and_match_shapes_agree() -> None:
    assert (so.Rectangle(3.0, 4.0).area()
            == sm.area(sm.Rectangle(3.0, 4.0)))
    assert so.Circle(1.0).area() == sm.area(sm.Circle(1.0))
