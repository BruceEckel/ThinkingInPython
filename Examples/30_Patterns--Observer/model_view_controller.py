# model_view_controller.py
from counter_model import Counter
from history_model import History
from record import record

@record
class CountView:
    model: Counter

    def __post_init__(self) -> None:
        self.model.connect(self.display)

    def display(self, count: int) -> None:
        print(f"count: {count}")

@record
class HistoryView:
    model: History

    def __post_init__(self) -> None:
        self.model.connect(self.display)

    def display(self, keys: str) -> None:
        print(f"keys: {keys}")

@record
class Controller:  # Interprets but doesn't display
    counter: Counter
    history: History

    def key(self, char: str) -> None:
        self.history.add(char)
        match char:
            case "+":
                self.counter.increment()
            case "-":
                self.counter.decrement()
            case _:
                pass

@record
class VimController:  # k is up, j is down
    counter: Counter
    history: History

    def key(self, char: str) -> None:
        self.history.add(char)
        match char:
            case "k":
                self.counter.increment()
            case "j":
                self.counter.decrement()
            case _:
                pass

counter = Counter()
history = History()
count_view = CountView(counter)
history_view = HistoryView(history)
controller = Controller(counter, history)
for char in "++-x":
    controller.key(char)
#: keys: +
#: count: 1
#: keys: ++
#: count: 2
#: keys: ++-
#: count: 1
#: keys: ++-x
vim = VimController(counter, history)  # Same models
for char in "kkj":
    vim.key(char)
#: keys: ++-xk
#: count: 2
#: keys: ++-xkk
#: count: 3
#: keys: ++-xkkj
#: count: 2
