# paper_scissors_rock.py
from typing import Any
from arena import all_pairs, duel
from outcome import Outcome

class Item:
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def compete(self, opponent: Any) -> Outcome:
        # First dispatch: self was Paper
        return opponent.eval_paper(self)
    def eval_paper(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Paper, and it draws
        return Outcome.DRAW
    def eval_scissors(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Scissors, and it wins
        return Outcome.WIN
    def eval_rock(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Rock, and it loses
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, opponent: Any) -> Outcome:
        # First dispatch: self was Scissors
        return opponent.eval_scissors(self)
    def eval_paper(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Paper, and it loses
        return Outcome.LOSE
    def eval_scissors(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Scissors, and it draws
        return Outcome.DRAW
    def eval_rock(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Rock, and it wins
        return Outcome.WIN

class Rock(Item):
    def compete(self, opponent: Any) -> Outcome:
        # First dispatch: self was Rock
        return opponent.eval_rock(self)
    def eval_paper(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Paper, and it wins
        return Outcome.WIN
    def eval_scissors(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Scissors, and it loses
        return Outcome.LOSE
    def eval_rock(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Rock, and it draws
        return Outcome.DRAW

if __name__ == "__main__":
    for player, opponent in all_pairs(Item):
        duel(player, opponent)
#: Paper <--> Paper : draw
#: Paper <--> Scissors : lose
#: Paper <--> Rock : win
#: Scissors <--> Paper : win
#: Scissors <--> Scissors : draw
#: Scissors <--> Rock : lose
#: Rock <--> Paper : lose
#: Rock <--> Scissors : win
#: Rock <--> Rock : draw
