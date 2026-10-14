# pizza_direct.py
from record import record

@record
class Pizza:
    size: int = 12
    cheese: bool = True
    toppings: tuple[str, ...] = ()
