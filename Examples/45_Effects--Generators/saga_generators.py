# saga_generators.py
from collections.abc import Generator
from exceptions import expect

class Failed(Exception):
    pass

type Commands = Generator[str]

def commands(*names: str) -> Commands:
    yield from names

def step(
    *, do: Commands, undo: Commands,
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
        do=commands("reserve seat", "issue ticket"),
        undo=commands("void ticket", "release seat"),
        rest=step(
            do=commands("hold room"),
            undo=commands("release room"),
            rest=step(
                do=commands("book taxi"),
                undo=commands("cancel taxi"),
                rest=step(
                    do=commands("charge card"),
                    undo=commands("refund card"),
                ),
            ),
        ),
    )

print(*book(), sep="\n")
#: reserve seat
#: issue ticket
#: hold room
#: book taxi
#: charge card
booking = book()
print([next(booking) for _ in range(4)][-1])
#: book taxi
print(booking.throw(Failed("no taxi")))  # [2]
#: release room
print(next(booking))
#: void ticket
print(next(booking))
#: release seat
expect(Failed, next, booking)  # [3]
#: [Failed] no taxi
