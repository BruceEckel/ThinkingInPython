# exercise_5_rejected.py
from dataclasses import dataclass

try:
    @dataclass
    class Cart:
        items: list[str] = []

except ValueError as e:
    print(type(e).__name__)
    print(str(e).partition(" for ")[0])
#: ValueError
#: mutable default <class 'list'>
