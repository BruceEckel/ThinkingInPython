# trace_cm.py
from typing import Self

class Trace:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> Self:
        print(f"enter {self.name}")
        return self

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: object, tb: object) -> None:
        print(f"exit {self.name}")

if __name__ == "__main__":
    with Trace("A") as t:
        print(f"inside {t.name}")
#: enter A
#: inside A
#: exit A
