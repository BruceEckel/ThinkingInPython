# saga_generators.py
from collections.abc import Generator
from exceptions import expect

class Failed(Exception):
    pass

type Commands = Generator[str]

def commands(*names: str) -> Commands:
    yield from names

def step(
    do: Commands, undo: Commands,
    rest: Commands | None = None,
) -> Commands:
    yield from do
    if rest is None:
        return
    try:
        yield from rest
    except Failed:
        yield from undo  # [1]
        raise

def book() -> Commands:
    return step(
        commands("reserve seat", "issue ticket"),
        commands("void ticket", "release seat"),
        step(commands("hold room"),
             commands("release room"),
             step(commands("charge card"),
                  commands("refund card"))),
    )

print(*book(), sep=", ")
#: reserve seat, issue ticket, hold room, charge card
booking = book()
print([next(booking) for _ in range(4)][-1])
#: charge card
print(booking.throw(Failed("card declined")))  # [2]
#: release room
print(next(booking))
#: void ticket
print(next(booking))
#: release seat
expect(Failed, next, booking)  # [3]
#: [Failed] card declined
