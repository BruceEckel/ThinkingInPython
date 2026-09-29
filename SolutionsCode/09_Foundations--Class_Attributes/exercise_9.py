# exercise_9.py
from exceptions import expected

class Ticket:
    seat: str  # Declared, assigned by no method

    def __init__(self, holder: str) -> None:
        self.holder = holder

t = Ticket("Ada")
print(vars(t))
#: {'holder': 'Ada'}
with expected(AttributeError):
    print(t.seat)
#: [AttributeError] 'Ticket' object has no attribute 'seat'
t.seat = "14C"
print(vars(t), t.seat)
#: {'holder': 'Ada', 'seat': '14C'} 14C
