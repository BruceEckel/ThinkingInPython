# test_grid_observer.py
from grid_observer import (Color, Grid, GridModel,
                          new_grid, recolored)

def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == Color.SKYBLUE
    # Same (x + y) color band
    assert grid[(0, 1)] == grid[(1, 0)]

def test_next_steps_and_wraps() -> None:
    assert Color.SKYBLUE.next() == Color.PALEGREEN
    assert Color.KHAKI.next() == Color.SKYBLUE

def test_recolored_changes_the_cross() -> None:
    grid = new_grid(3)
    out = recolored(grid, (1, 1))
    cross = {(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)}
    assert all(out[c] == grid[c].next() for c in cross)
    assert all(out[c] == grid[c]
               for c in grid if c not in cross)
    assert out is not grid
    assert grid == new_grid(3)

def test_corner_selection_stays_on_the_grid() -> None:
    grid = new_grid(3)
    out = recolored(grid, (0, 0))
    changed = {c for c in grid if out[c] != grid[c]}
    assert changed == {(0, 0), (1, 0), (0, 1)}
    assert out.keys() == grid.keys()

def test_responders_receive_the_new_grid() -> None:
    model = GridModel(3)
    before = model.grid[(1, 1)]
    seen: list[Grid] = []
    model.connect(seen.append)
    model.select((1, 1))
    assert len(seen) == 1
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] != before
