# yield_from_levels.py
from collections.abc import Generator
from record import record

@record
class RMsg:
    s: str

@record
class YMsg:
    s: str

def inner() -> Generator[YMsg, None, RMsg]:
    yield YMsg("inner A")
    yield YMsg("inner B")
    return RMsg("Message from inner!")

def middle() -> Generator[YMsg, None, RMsg]:
    yield YMsg("middle A")
    yield YMsg("middle B")
    return (yield from inner())

def outer() -> Generator[YMsg, None, RMsg]:
    yield YMsg("outer A")
    yield YMsg("outer B")
    return (yield from middle())

def report() -> Generator[YMsg]:
    result = yield from outer()
    yield YMsg(str(result))

for line in report():
    print(line)
#: YMsg(s='outer A')
#: YMsg(s='outer B')
#: YMsg(s='middle A')
#: YMsg(s='middle B')
#: YMsg(s='inner A')
#: YMsg(s='inner B')
#: YMsg(s="RMsg(s='Message from inner!')")
