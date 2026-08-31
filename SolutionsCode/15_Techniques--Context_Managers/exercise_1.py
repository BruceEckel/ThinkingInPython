# exercise_1.py
from typing import Self

class Trace:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> Self:
        print(f"enter {self.name}")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        print(f"exit {self.name}")

with Trace("A") as t:
    print(f"inside {t.name}")
    with Trace("B") as u:
        print(f"inside {u.name}")
#: enter A
#: inside A
#: enter B
#: inside B
#: exit B
#: exit A
