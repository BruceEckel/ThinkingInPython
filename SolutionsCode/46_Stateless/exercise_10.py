# exercise_10.py
from typing import Final
from stateless import Effect, Need, need, run, supply, throws

class Console:
    def print(self, message: str) -> None:
        print(message)

SCORES: Final[dict[str, int]] = {"Alice": 42, "Bob": 7, "Cyd": -3}

@throws(KeyError)
def score(name: str) -> int:
    return SCORES[name]

@throws(ValueError)
def format_score(name: str, value: int) -> str:
    if value < 0:
        raise ValueError(f"negative score for {name}: {value}")
    return f"{name}: {value}"

def announce(
    name: str,
) -> Effect[Need[Console], KeyError | ValueError, None]:
    value: int = yield from score(name)
    line: str = yield from format_score(name, value)
    console = yield from need(Console)
    console.print(line)

bound = supply(Console())(announce)
for who in ("Alice", "Cyd", "Dana"):
    try:
        run(bound(who))
    except (KeyError, ValueError) as e:
        print(f"{type(e).__name__}: {e}")
#: Alice: 42
#: ValueError: negative score for Cyd: -3
#: KeyError: 'Dana'
