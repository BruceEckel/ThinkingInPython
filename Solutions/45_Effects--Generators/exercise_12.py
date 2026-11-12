# exercise_12.py
from collections.abc import Generator

class Failed(Exception):
    pass

type Commands = Generator[str]

def commands(*names: str) -> Commands:
    yield from names

def step(
    do: Commands, undo: Commands,
    rest: Commands | None = None,
) -> Commands:
    try:
        yield from do  # [1]
        if rest is not None:
            yield from rest
    except Failed:
        yield from undo
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

def unwind(saga: Commands, error: Failed) -> None:
    try:
        print(saga.throw(error))
        for command in saga:
            print(command)
    except Failed as e:
        print(f"Failed: {e}")

booking = book()
print([next(booking) for _ in range(2)][-1])
#: issue ticket
unwind(booking, Failed("printer jammed"))  # [2]
#: void ticket
#: release seat
#: Failed: printer jammed
booking = book()
print([next(booking) for _ in range(4)][-1])
#: charge card
unwind(booking, Failed("card declined"))  # [3]
#: refund card
#: release room
#: void ticket
#: release seat
#: Failed: card declined
