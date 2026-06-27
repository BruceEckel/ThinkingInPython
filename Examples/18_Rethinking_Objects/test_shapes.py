# test_shapes.py
import shapes_match as sm
import shapes_oo as so

def test_oo_and_match_shapes_agree() -> None:
    assert (so.Rectangle(3.0, 4.0).area()
            == sm.area(sm.Rectangle(3.0, 4.0)))
    assert so.Circle(1.0).area() == sm.area(sm.Circle(1.0))
