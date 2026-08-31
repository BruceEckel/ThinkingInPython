# exercise_2_reorder.py
from typing import final, override

class Framework:
    def __init__(self) -> None:
        self.run()

    @final
    def run(self) -> None:
        self.step()

    def step(self) -> None: ...

class Greeter(Framework):
    def __init__(self, name: str) -> None:
        self.name = name  # Setup first...
        super().__init__()  # ...then start the engine

    @override
    def step(self) -> None:
        print(f"Hello, {self.name}!")

Greeter("Brian")
#: Hello, Brian!
