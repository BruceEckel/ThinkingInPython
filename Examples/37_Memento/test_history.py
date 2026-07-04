# test_history.py
from history import History

def test_undo_and_redo() -> None:
    history = History(0)
    history.do(1)
    history.do(2)
    assert history.undo() == 1
    assert history.undo() == 0
    assert history.redo() == 1

def test_new_action_clears_redo() -> None:
    history = History("a")
    history.do("ab")
    history.undo()
    history.do("ax")
    assert not history.can_redo()
    assert history.present == "ax"

def test_bounds_are_reported() -> None:
    history = History(0)
    assert not history.can_undo()
    history.do(1)
    assert history.can_undo() and not history.can_redo()
    history.undo()
    assert history.can_redo() and not history.can_undo()
