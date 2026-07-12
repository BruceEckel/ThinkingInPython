# comparing_ordinary_to_data_classes.py
from display import REDEFINED_DUNDERS, display_object

def show(obj: object) -> None:
    display_object(obj, REDEFINED_DUNDERS)

class A:
    x: int
    s: str

show(A)
#: === A ===
#: [Attributes]
#:   None
#: [Methods]
#:   None
