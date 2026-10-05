# test_init_subclass.py
import init_subclass

def test_color_registry_holds_only_leaves() -> None:
    leaves = {c.__name__
              for c in init_subclass.Color.registry}
    assert leaves == {"Red", "Green", "PhthaloBlue",
                      "CeruleanBlue"}

def test_independent_hierarchies_have_separate_registries(
) -> None:
    shapes = {c.__name__
              for c in init_subclass.Shape.registry}
    assert "Round" not in shapes
    assert shapes == {"Square", "Circle"}
    # Neither registry leaks into the other
    assert init_subclass.Shape.registry.isdisjoint(
        init_subclass.Color.registry)
