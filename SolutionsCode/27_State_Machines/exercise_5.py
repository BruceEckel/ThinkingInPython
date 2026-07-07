# exercise_5.py
TRANSITIONS: dict[tuple[str, str], str] = {
    ("locked", "coin"): "unlocked",
    ("locked", "push"): "locked",
    ("unlocked", "push"): "locked",
    ("unlocked", "coin"): "unlocked",
}

class TableController:
    def __init__(self, initial: str,
                 table: dict[tuple[str, str], str]) -> None:
        self.current = initial
        self.table = table

    def process(self, word: str) -> None:
        self.current = self.table[self.current, word]

words = ["push", "coin", "push", "coin", "coin", "push"]
tc = TableController("locked", TRANSITIONS)
history = [tc.current]
for word in words:
    tc.process(word)
    history.append(tc.current)
print(" ".join(history))
#: locked locked unlocked locked unlocked unlocked locked
