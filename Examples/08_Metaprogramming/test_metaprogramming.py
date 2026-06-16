# test_metaprogramming.py
import pytest
import final
import init_subclass
import set_name


def test_leaf_registry_tracks_only_leaves() -> None:
    leaves = {c.__name__ for c in init_subclass.Color.registry}
    assert leaves == {"Red", "Green", "PhthaloBlue", "CeruleanBlue"}


def test_independent_hierarchies_have_separate_registries() -> None:
    shapes = {c.__name__ for c in init_subclass.Shape.registry}
    assert shapes == {"Square", "Circle"}  # Round is no longer a leaf


def test_descriptor_learns_its_name() -> None:
    p = set_name.Point()
    p.x = 3
    p.y = 4
    assert (p.x, p.y) == (3, 4)
    assert p.__dict__ == {"_x": 3, "_y": 4}  # stored under the names


def test_descriptor_on_class_returns_itself() -> None:
    assert isinstance(set_name.Point.x, set_name.Field)


def test_final_class_cannot_be_subclassed() -> None:
    with pytest.raises(TypeError):
        class Sub(final.B):
            pass


def test_non_final_base_can_be_subclassed() -> None:
    class Ok(final.A):
        pass

    assert issubclass(Ok, final.A)
