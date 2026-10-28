# exercise_3.py
from types import ModuleType
from typing import Final
import exercise_1 as table
import exercise_2 as methods
from exercise_1 import Outcome

type Name = str

EXPECTED: Final[dict[tuple[Name, Name], Outcome]] = {
    ("Paper", "Rock"): Outcome.WIN,
    ("Paper", "Scissors"): Outcome.LOSE,
    ("Paper", "Paper"): Outcome.DRAW,
    ("Paper", "Lizard"): Outcome.LOSE,
    ("Scissors", "Paper"): Outcome.WIN,
    ("Scissors", "Rock"): Outcome.LOSE,
    ("Scissors", "Scissors"): Outcome.DRAW,
    ("Scissors", "Lizard"): Outcome.LOSE,
    ("Rock", "Scissors"): Outcome.WIN,
    ("Rock", "Paper"): Outcome.LOSE,
    ("Rock", "Rock"): Outcome.DRAW,
    ("Rock", "Lizard"): Outcome.WIN,
    ("Lizard", "Paper"): Outcome.WIN,
    ("Lizard", "Scissors"): Outcome.WIN,
    ("Lizard", "Rock"): Outcome.LOSE,
    ("Lizard", "Lizard"): Outcome.DRAW,
}

def compete(module: ModuleType, player: Name,
            opponent: Name) -> str:
    result = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, module.Outcome)
    return result

for module in (table, methods):
    wrong = [pair for pair, result in EXPECTED.items()
             if compete(module, *pair) != result]
    print(module.__name__, len(EXPECTED), "agree:",
          not wrong)
#: exercise_1 16 agree: True
#: exercise_2 16 agree: True
