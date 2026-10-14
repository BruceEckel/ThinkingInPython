# exercise_5.py
import random
from collections.abc import Iterator
from enum import StrEnum

class Mouse(StrEnum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"

NEXT_ACTIONS: dict[Mouse | None,
                   list[Mouse]] = {
    None: [Mouse.APPEARS],
    Mouse.APPEARS: [Mouse.RUNS_AWAY,
                          Mouse.ENTERS],
    Mouse.RUNS_AWAY: [Mouse.APPEARS],
    Mouse.ENTERS: [Mouse.ESCAPES,
                         Mouse.TRAPPED],
    Mouse.ESCAPES: [Mouse.APPEARS],
    Mouse.TRAPPED: [Mouse.REMOVED],
    Mouse.REMOVED: [Mouse.APPEARS],
}

def mouse_move_generator(
    count: int, seed: int = 0
) -> Iterator[Mouse]:
    rng = random.Random(seed)
    previous: Mouse | None = None
    for _ in range(count):
        previous = rng.choice(NEXT_ACTIONS[previous])
        yield previous

moves = list(mouse_move_generator(8, seed=1))
print(" ".join(m.name for m in moves[:4]))
#: APPEARS RUNS_AWAY APPEARS RUNS_AWAY
print(" ".join(m.name for m in moves[4:]))
#: APPEARS ENTERS TRAPPED REMOVED
