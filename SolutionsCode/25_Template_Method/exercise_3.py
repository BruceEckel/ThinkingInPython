# exercise_3.py
from typing import final, override

class ApplicationFramework:
    def __init__(self) -> None:
        self.run()

    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

class Reversed(ApplicationFramework):
    @override
    def run(self) -> None:  # type: ignore
        for _ in range(2):
            self.customize2()
            self.customize1()

    @override
    def customize1(self) -> None:
        print("one")

    @override
    def customize2(self) -> None:
        print("two")

Reversed()
#: two
#: one
#: two
#: one
