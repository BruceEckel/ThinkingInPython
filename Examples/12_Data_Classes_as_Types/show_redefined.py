# show_redefined.py
from display import REDEFINED_DUNDERS, display_object

def show(obj: object) -> None:
    display_object(obj, REDEFINED_DUNDERS, exclude=("__hash__",))
