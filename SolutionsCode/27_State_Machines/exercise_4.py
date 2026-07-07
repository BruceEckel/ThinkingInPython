# exercise_4.py
from __future__ import annotations

class Controller:
    def __init__(self, initial: str) -> None:
        self.states: dict[str, WordState] = {}
        self.current = initial

    def register(self, name: str, state: WordState) -> None:
        self.states[name] = state

    def process(self, word: str) -> None:
        state = self.states[self.current]
        self.current = state.next_state(word)

class WordState:
    TRANSITIONS: dict[str, str] = {}

    def next_state(self, word: str) -> str:
        return self.TRANSITIONS.get(word, self.TRANSITIONS["*"])

class Locked(WordState):
    TRANSITIONS = {"coin": "unlocked", "*": "locked"}

class Unlocked(WordState):
    TRANSITIONS = {"push": "locked", "*": "unlocked"}

controller = Controller("locked")
controller.register("locked", Locked())
controller.register("unlocked", Unlocked())

words = ["push", "coin", "push", "coin", "coin", "push"]
history = [controller.current]
for word in words:
    controller.process(word)
    history.append(controller.current)
print(" ".join(history))
#: locked locked unlocked locked unlocked unlocked locked
