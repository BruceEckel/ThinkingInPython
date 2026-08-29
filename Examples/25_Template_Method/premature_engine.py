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
        # With the usual style, the engine calls run()
        super().__init__()
        self.name = name  # ...before this line runs

    @override
    def step(self) -> None:
        print(f"Hello, {self.name}!")

try:
    Greeter("Robin")
except AttributeError as e:
    print(e)
#: 'Greeter' object has no attribute 'name'
