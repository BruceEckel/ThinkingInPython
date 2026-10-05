# test_set_name.py
import set_name

def test_descriptor_learns_its_name() -> None:
    field = vars(set_name.Point)["x"]
    assert field.name == "x"
    assert field.storage == "_x"

def test_values_stored_under_storage_keys() -> None:
    p = set_name.Point()
    p.x = 3
    p.y = 4
    assert (p.x, p.y) == (3, 4)
    assert p.__dict__ == {"_x": 3, "_y": 4}

def test_descriptor_on_class_returns_itself() -> None:
    assert isinstance(set_name.Point.x, set_name.Field)
    assert set_name.Point.x is vars(set_name.Point)["x"]
