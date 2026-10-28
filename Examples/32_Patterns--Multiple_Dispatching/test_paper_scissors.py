# test_paper_scissors.py
from types import ModuleType
from typing import Final
import paper_scissors_rock as methods
import paper_scissors_rock_table as table
import pytest
from outcome import Outcome

type Name = str

# (player, opponent): the player's result
EXPECTED: Final[dict[tuple[Name, Name], Outcome]] = {
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

def compete(module: ModuleType, player: Name,
            opponent: Name) -> Outcome:
    result: Outcome = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, Outcome)
    return result

@pytest.mark.parametrize("module", [table, methods])
@pytest.mark.parametrize("player, opponent", EXPECTED)
def test_versions_match_expected(module: ModuleType,
                                 player: Name,
                                 opponent: Name) -> None:
    expected = EXPECTED[player, opponent]
    assert compete(module, player, opponent) == expected
