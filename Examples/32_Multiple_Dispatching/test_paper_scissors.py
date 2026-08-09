# test_paper_scissors.py
from types import ModuleType
from typing import Final
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

def compete(module: ModuleType, player: str,
            opponent: str) -> Outcome:
    result: Outcome = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, Outcome)
    return result

MATCHUPS: Final[list[tuple[str, str, Outcome]]] = [
    (p, o, r) for (p, o), r in EXPECTED.items()
]

@pytest.mark.parametrize("module", [table, methods])
@pytest.mark.parametrize("player, opponent, expected", MATCHUPS)
def test_matches_expected(module: ModuleType, player: str,
                          opponent: str, expected: Outcome) -> None:
    assert compete(module, player, opponent) == expected

@pytest.mark.parametrize("player, opponent, expected", MATCHUPS)
def test_both_versions_agree(player: str, opponent: str,
                             expected: Outcome) -> None:
    assert (compete(methods, player, opponent)
            == compete(table, player, opponent))

@pytest.mark.parametrize("outcome, expected", [
    (Outcome.WIN, "win"),
    (Outcome.LOSE, "lose"),
    (Outcome.DRAW, "draw"),
])
def test_outcome_str(outcome: Outcome, expected: str) -> None:
    assert str(outcome) == expected
