# exercise_13.py
from collections.abc import Callable
from record import record

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def connect(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)

class Counter(Broadcaster[int]):
    def __init__(self) -> None:
        super().__init__()
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def increment(self) -> None:
        self._count += 1
        self.announce(self._count)

    def decrement(self) -> None:
        self._count -= 1
        self.announce(self._count)

@record
class View:
    model: Counter

    def __post_init__(self) -> None:
        self.model.connect(self.display)

    def display(self, count: int) -> None:
        print(f"count: {count}")

@record
class BarView:
    model: Counter

    def __post_init__(self) -> None:
        self.model.connect(self.display)

    def display(self, count: int) -> None:
        print(f"[{'*' * count}]")

@record
class VimController:  # k is up, j is down
    model: Counter

    def key(self, char: str) -> None:
        match char:
            case "k":
                self.model.increment()
            case "j":
                self.model.decrement()
            case _:
                pass

model = Counter()
view = View(model)
bar = BarView(model)
vim = VimController(model)
for char in "kkj":
    vim.key(char)
#: count: 1
#: [*]
#: count: 2
#: [**]
#: count: 1
#: [*]
