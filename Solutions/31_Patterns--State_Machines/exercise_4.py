# exercise_4.py
type StateName = str
type Word = str
type Transitions = dict[tuple[StateName, Word], StateName]

TRANSITIONS: Transitions = {
    ("locked", "coin"): "unlocked",
    ("locked", "push"): "locked",
    ("unlocked", "push"): "locked",
    ("unlocked", "coin"): "unlocked",
}

class TableController:
    def __init__(self, initial: StateName,
                 table: Transitions) -> None:
        self.current = initial
        self.table = table

    def process(self, word: Word) -> None:
        self.current = self.table[self.current, word]

words = ["push", "coin", "push", "coin", "coin", "push"]
tc = TableController("locked", TRANSITIONS)
history = [tc.current]
for word in words:
    tc.process(word)
    history.append(tc.current)
print(" ".join(history))
#: locked locked unlocked locked unlocked unlocked locked
