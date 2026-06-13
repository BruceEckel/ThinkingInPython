# StateMachine/mouse/MouseAction.py

class MouseAction:
    appears: "MouseAction"
    runsAway: "MouseAction"
    enters: "MouseAction"
    escapes: "MouseAction"
    trapped: "MouseAction"
    removed: "MouseAction"

    def __init__(self, action: str) -> None:
        self.action = action
    def __str__(self) -> str: return self.action
    def __eq__(self, other: object) -> bool:
        return (isinstance(other, MouseAction)
                and self.action == other.action)
    # Necessary when __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self) -> int:
        return hash(self.action)

# Static fields; an enumeration of instances:
MouseAction.appears = MouseAction("mouse appears")
MouseAction.runsAway = MouseAction("mouse runs away")
MouseAction.enters = MouseAction("mouse enters trap")
MouseAction.escapes = MouseAction("mouse escapes")
MouseAction.trapped = MouseAction("mouse trapped")
MouseAction.removed = MouseAction("mouse removed")
