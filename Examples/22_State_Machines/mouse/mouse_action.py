# mouse/mouse_action.py
from enum import Enum


class MouseAction(Enum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"

    def __str__(self) -> str:
        return self.value
