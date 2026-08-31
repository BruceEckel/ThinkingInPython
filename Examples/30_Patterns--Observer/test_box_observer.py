# test_box_observer.py
from box_observer import (BoxModel, Grid, adjacent,
                          new_grid, recolored)

def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == "skyblue"  # COLORS[0]
    # Same (x + y) color band
    assert grid[(0, 1)] == grid[(1, 0)]

def test_adjacent() -> None:
    assert adjacent((1, 1), (2, 2))  # Diagonal
    assert adjacent((1, 1), (1, 2))  # Edge
    # Not its own neighbor
    assert not adjacent((1, 1), (1, 1))
    assert not adjacent((0, 0), (2, 0))  # Two away

def test_recolored_touches_only_neighbors() -> None:
    grid = new_grid(5)
    out = recolored(grid, (2, 2))
    # Diagonal neighbor: changed
    assert out[(1, 1)] == grid[(2, 2)]
    # Edge neighbor: changed
    assert out[(2, 3)] == grid[(2, 2)]
    # Two away: unchanged
    assert out[(0, 0)] == grid[(0, 0)]
    assert out is not grid  # Pure: a new grid

def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(5)
    seen: list[Grid] = []
    # The observer is a callable
    model.subscribe(seen.append)
    model.click((2, 2))
    # Observer got the new grid
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] == model.grid[(2, 2)]
