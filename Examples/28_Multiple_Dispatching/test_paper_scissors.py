# test_paper_scissors.py
from typing import Any
import paper_scissors_rock as methods
import paper_scissors_rock2 as table
from outcome import Outcome

# (player, opponent): the player's result
EXPECTED = {
    ("Paper", "Rock"): Outcome.WIN,
    ("Paper", "Scissors"): Outcome.LOSE,
    ("Paper", "Paper"): Outcome.DRAW,
    ("Scissors", "Paper"): Outcome.WIN,
    ("Scissors", "Rock"): Outcome.LOSE,
    ("Scissors", "Scissors"): Outcome.DRAW,
    ("Rock", "Scissors"): Outcome.WIN,
    ("Rock", "Paper"): Outcome.LOSE,
    ("Rock", "Rock"): Outcome.DRAW,
}

def compete(module: Any, player: str, opponent: str) -> Outcome:
    result = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, Outcome)
    return result

def test_table_version_matches_expected() -> None:
    for (player, opponent), result in EXPECTED.items():
        assert compete(table, player, opponent) == result

def test_method_version_matches_expected() -> None:
    for (player, opponent), result in EXPECTED.items():
        assert compete(methods, player, opponent) == result

def test_both_versions_agree() -> None:
    for player, opponent in EXPECTED:
        assert (compete(methods, player, opponent)
                == compete(table, player, opponent))

def test_outcome_str() -> None:
    assert str(Outcome.WIN) == "win"
    assert str(Outcome.LOSE) == "lose"
    assert str(Outcome.DRAW) == "draw"
