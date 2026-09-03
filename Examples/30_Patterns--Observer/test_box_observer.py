# test_box_observer.py
from box_observer import (COLORS, BoxModel, Grid,
                          new_grid, recolored)

def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == "skyblue"  # COLORS[0]
    # Same (x + y) color band
    assert grid[(0, 1)] == grid[(1, 0)]

def test_recolored_changes_one_cell() -> None:
    grid = new_grid(3)
    out = recolored(grid, (1, 1))
    # The clicked cell takes the next color
    was = COLORS.index(grid[(1, 1)])
    assert out[(1, 1)] == COLORS[(was + 1) % 3]
    assert all(out[c] == grid[c]
               for c in grid if c != (1, 1))
    assert out is not grid  # Pure: a new grid

def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(3)
    before = model.grid[(1, 1)]
    seen: list[Grid] = []
    # The observer is a callable
    model.subscribe(seen.append)
    model.click((1, 1))
    # Observer got the new grid
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] != before
