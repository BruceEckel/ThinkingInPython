# test_box_observer.py
from box_observer import (BoxModel, Grid, new_grid,
                          next_color, recolored)

def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == "skyblue"  # COLORS[0]
    # Same (x + y) color band
    assert grid[(0, 1)] == grid[(1, 0)]

def test_next_color_wraps() -> None:
    assert next_color("skyblue") == "palegreen"
    assert next_color("khaki") == "skyblue"

def test_recolored_changes_the_cross() -> None:
    grid = new_grid(3)
    out = recolored(grid, (1, 1))
    cross = {(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)}
    assert all(out[c] == next_color(grid[c])
               for c in cross)
    assert all(out[c] == grid[c]
               for c in grid if c not in cross)
    assert out is not grid  # Pure: a new grid

def test_corner_click_stays_on_the_grid() -> None:
    grid = new_grid(3)
    out = recolored(grid, (0, 0))
    changed = {c for c in grid if out[c] != grid[c]}
    assert changed == {(0, 0), (1, 0), (0, 1)}
    assert out.keys() == grid.keys()

def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(3)
    before = model.grid[(1, 1)]
    seen: list[Grid] = []
    # The observer is a callable
    model.subscribe(seen.append)
    model.click((1, 1))
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] != before
