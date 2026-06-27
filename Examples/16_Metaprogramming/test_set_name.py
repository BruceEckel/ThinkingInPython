# test_set_name.py
import set_name

def test_descriptor_learns_its_name() -> None:
    p = set_name.Point()
    p.x = 3
    p.y = 4
    assert (p.x, p.y) == (3, 4)
    assert p.__dict__ == {"_x": 3, "_y": 4}  # Stored under the names

def test_descriptor_on_class_returns_itself() -> None:
    assert isinstance(set_name.Point.x, set_name.Field)
