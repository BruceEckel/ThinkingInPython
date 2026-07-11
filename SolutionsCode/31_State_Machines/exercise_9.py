# exercise_9.py
import random
from collections.abc import Iterator
from enum import StrEnum

class MouseAction(StrEnum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"

NEXT_ACTIONS: dict[MouseAction | None, list[MouseAction]] = {
    None: [MouseAction.APPEARS],
    MouseAction.APPEARS: [MouseAction.RUNS_AWAY, MouseAction.ENTERS],
    MouseAction.RUNS_AWAY: [MouseAction.APPEARS],
    MouseAction.ENTERS: [MouseAction.ESCAPES, MouseAction.TRAPPED],
    MouseAction.ESCAPES: [MouseAction.APPEARS],
    MouseAction.TRAPPED: [MouseAction.REMOVED],
    MouseAction.REMOVED: [MouseAction.APPEARS],
}

def mouse_move_generator(
    count: int, seed: int = 0
) -> Iterator[MouseAction]:
    rng = random.Random(seed)
    previous: MouseAction | None = None
    for _ in range(count):
        previous = rng.choice(NEXT_ACTIONS[previous])
        yield previous

moves = list(mouse_move_generator(8, seed=1))
print(" ".join(m.name for m in moves))
#: APPEARS RUNS_AWAY APPEARS RUNS_AWAY APPEARS ENTERS TRAPPED REMOVED
