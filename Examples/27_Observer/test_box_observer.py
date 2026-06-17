# test_box_observer.py
from typing import Any

from box_observer import BoxModel, adjacent, new_grid, recolored
from observer import Observer


def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == "skyblue"     # COLORS[0]
    assert grid[(0, 1)] == grid[(1, 0)]  # same (x + y) color band


def test_adjacent() -> None:
    assert adjacent((1, 1), (2, 2))      # diagonal
    assert adjacent((1, 1), (1, 2))      # edge
    assert not adjacent((1, 1), (1, 1))  # not its own neighbor
    assert not adjacent((0, 0), (2, 0))  # two away


def test_recolored_touches_only_neighbors() -> None:
    grid = new_grid(5)
    out = recolored(grid, (2, 2))
    assert out[(1, 1)] == grid[(2, 2)]   # diagonal neighbor: changed
    assert out[(2, 3)] == grid[(2, 2)]   # edge neighbor: changed
    assert out[(0, 0)] == grid[(0, 0)]   # two away: unchanged
    assert out is not grid               # pure: a new grid


def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(5)
    seen: list[Any] = []

    class Recorder(Observer):
        def update(self, observable: Any, grid: Any) -> None:
            seen.append(grid)

    model.add_observer(Recorder())
    model.click((2, 2))
    assert seen[-1] is model.grid        # observer got the new grid
    assert model.grid[(1, 1)] == model.grid[(2, 2)]
