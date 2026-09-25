# paper_scissors_rock_subclass.py
from typing import Any
from outcome import Outcome
from paper_scissors_rock import Paper, Rock, Scissors

class DampPaper(Paper):
    def compete(self, item: Any) -> Outcome:
        if isinstance(item, Rock):
            return Outcome.DRAW  # Too soggy to wrap
        return super().compete(item)
    def eval_rock(self, item: Any) -> Outcome:
        return Outcome.DRAW  # Rock's side of the same draw

print(DampPaper().compete(Rock()))
#: draw
print(Rock().compete(DampPaper()))
#: draw
print(DampPaper().compete(Scissors()))
#: lose
