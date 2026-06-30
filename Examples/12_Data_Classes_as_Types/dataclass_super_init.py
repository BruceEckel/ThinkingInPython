# dataclass_super_init.py
from dataclasses import dataclass

class Connection:
    def __init__(self) -> None:
        self.open = True

@dataclass
class Logged(Connection):
    name: str

    def __post_init__(self) -> None:
        super().__init__()   # Run the base initializer explicitly

c = Logged("db")
print(c.name, c.open)
#: db True
