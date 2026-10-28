# exercise_3.py
from collections.abc import Callable
from enum import Enum
from record import record

type StateName = str
type Word = str
type Next = Callable[[Word], Turnstile]

@record
class WordRow:
    next: Next

def table(transitions: dict[Word, StateName]) -> Next:
    def next_state(word: Word) -> Turnstile:
        name = transitions.get(word, transitions["*"])
        return Turnstile[name]
    return next_state

class Turnstile(WordRow, Enum):
    LOCKED = (table({"coin": "UNLOCKED", "*": "LOCKED"}),)
    UNLOCKED = (table({"push": "LOCKED", "*": "UNLOCKED"}),)

    def __str__(self) -> str:
        return self.name.lower()

words = ["push", "coin", "push", "coin", "coin", "push"]
state = Turnstile.LOCKED
history = [state]
for word in words:
    state = state.next(word)
    history.append(state)
print(" ".join(str(s) for s in history))
#: locked locked unlocked locked unlocked unlocked locked
