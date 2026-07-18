# premature_engine.py
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
        super().__init__()  # Usual style: engine runs now...
        self.name = name  # ...before this line has happened

    @override
    def step(self) -> None:
        print(f"Hello, {self.name}!")

try:
    Greeter("Bruce")
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError
