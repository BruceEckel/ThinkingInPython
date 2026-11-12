# exercise_11.py
from collections.abc import Callable, Generator
from exceptions import expect

class Failed(Exception):
    pass

type Action = Callable[[], str]
type Undo = Callable[[], None]

def step(
    action: Action, undo: Undo,
    rest: Generator[str] | None = None,
) -> Generator[str]:
    yield action()  # [1]
    if rest is None:
        return
    try:
        yield from rest
    except Failed:
        undo()  # [2]
        raise

def doing(name: str) -> Action:
    return lambda: f"do {name}"

def undoing(name: str) -> Undo:
    return lambda: print(f"undo {name}")

def decline() -> str:
    raise Failed("card declined")

def book(card: Action) -> Generator[str]:
    return step(
        doing("flight"), undoing("flight"),
        step(doing("hotel"), undoing("hotel"),
             step(card, undoing("card"))),
    )

print(list(book(doing("card"))))
#: ['do flight', 'do hotel', 'do card']
booking = book(decline)
print(next(booking))
#: do flight
print(next(booking))
#: do hotel
expect(Failed, next, booking)  # [3]
#: undo hotel
#: undo flight
#: [Failed] card declined
