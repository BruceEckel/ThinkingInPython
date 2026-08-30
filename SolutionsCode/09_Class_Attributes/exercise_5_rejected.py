# exercise_5_rejected.py
from dataclasses import dataclass

try:
    @dataclass
    class Cart:
        items: list[str] = []

except ValueError as e:
    print(str(e).partition(" is not")[0])
    print(str(e).partition(" for ")[0])
#: mutable default <class 'list'> for field items
#: mutable default <class 'list'>
