# paper_scissors_rock_subclass.py
from typing import Any
from outcome import Outcome
from paper_scissors_rock import Paper, Rock, Scissors

class DampPaper(Paper):
    def compete(self, item: Any) -> Outcome:
        if isinstance(item, Rock):
            return Outcome.DRAW  # Too soggy to wrap
        return super().compete(item)

print(DampPaper().compete(Rock()))
#: draw
print(DampPaper().compete(Scissors()))
#: lose
