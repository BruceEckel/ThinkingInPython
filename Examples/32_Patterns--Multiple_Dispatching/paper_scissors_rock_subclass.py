# paper_scissors_rock_subclass.py
from typing import Any
from arena import duel
from outcome import Outcome
from paper_scissors_rock import Paper, Rock, Scissors

class DampPaper(Paper):
    def compete(self, opponent: Any) -> Outcome:
        if isinstance(opponent, Rock):
            return Outcome.DRAW  # Too soggy to wrap
        return super().compete(opponent)
    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.DRAW  # Rock's side of the same draw

duel(DampPaper(), Rock())
#: DampPaper <--> Rock : draw
duel(Rock(), DampPaper())
#: Rock <--> DampPaper : draw
duel(DampPaper(), Scissors())
#: DampPaper <--> Scissors : lose
