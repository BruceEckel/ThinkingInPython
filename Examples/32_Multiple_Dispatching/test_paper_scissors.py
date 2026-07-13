# test_paper_scissors.py
from typing import Any, Final
import paper_scissors_rock as methods
import paper_scissors_rock_table as table
import pytest
from outcome import Outcome

# (player, opponent): the player's result
EXPECTED: Final[dict[tuple[str, str], Outcome]] = {
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
    result: Outcome = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, Outcome)
    return result

@pytest.mark.parametrize("module", [table, methods])
def test_matches_expected(module: Any) -> None:
    for (player, opponent), result in EXPECTED.items():
        assert compete(module, player, opponent) == result

def test_both_versions_agree() -> None:
    for player, opponent in EXPECTED:
        assert (compete(methods, player, opponent)
                == compete(table, player, opponent))

@pytest.mark.parametrize("outcome, expected", [
    (Outcome.WIN, "win"),
    (Outcome.LOSE, "lose"),
    (Outcome.DRAW, "draw"),
])
def test_outcome_str(outcome: Outcome, expected: str) -> None:
    assert str(outcome) == expected
