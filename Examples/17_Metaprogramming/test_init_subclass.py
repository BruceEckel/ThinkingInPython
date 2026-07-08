# test_init_subclass.py
import init_subclass

def test_leaf_registry_tracks_only_leaves() -> None:
    leaves = {c.__name__ for c in init_subclass.Color.registry}
    assert leaves == {"Red", "Green", "PhthaloBlue", "CeruleanBlue"}

def test_independent_hierarchies_have_separate_registries() -> None:
    shapes = {c.__name__ for c in init_subclass.Shape.registry}
    assert shapes == {"Square", "Circle"}  # Round is no longer a leaf
