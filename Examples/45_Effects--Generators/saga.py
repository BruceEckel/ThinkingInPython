# saga.py
from collections.abc import Generator
from exceptions import expect

class Failed(Exception):
    pass

def step(
    name: str, rest: Generator[str] | None = None
) -> Generator[str]:
    yield f"do {name}"
    if rest is None:
        return
    try:
        yield from rest
    except Failed:
        print(f"undo {name}")
        raise

def book() -> Generator[str]:
    return step(
        "flight", step("hotel", step("taxi", step("card")))
    )

print(list(book()))
#: ['do flight', 'do hotel', 'do taxi', 'do card']
booking = book()
print(next(booking))
#: do flight
print(next(booking))
#: do hotel
print(next(booking))
#: do taxi
expect(Failed, booking.throw, Failed("no taxi"))
#: undo hotel
#: undo flight
#: [Failed] no taxi
