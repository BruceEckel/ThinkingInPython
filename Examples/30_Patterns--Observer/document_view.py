# document_view.py
from counter_model import Counter
from history_model import History
from record import record

@record
class View:
    counter: Counter
    history: History

    def __post_init__(self) -> None:
        self.counter.connect(self.display_count)
        self.history.connect(self.display_history)

    def display_count(self, count: int) -> None:
        print(f"count: {count}")

    def display_history(self, keys: str) -> None:
        print(f"keys: {keys}")

    def key(self, char: str) -> None:  # The controller
        self.history.add(char)
        match char:
            case "+":
                self.counter.increment()
            case "-":
                self.counter.decrement()
            case _:
                pass

view = View(Counter(), History())
for char in "++-x":
    view.key(char)
#: keys: +
#: count: 1
#: keys: ++
#: count: 2
#: keys: ++-
#: count: 1
#: keys: ++-x
