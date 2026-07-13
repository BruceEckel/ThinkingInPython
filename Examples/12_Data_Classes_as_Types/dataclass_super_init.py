# dataclass_super_init.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host

@dataclass
class Logged(Connection):
    host: str
    name: str

    def __post_init__(self) -> None:
        super().__init__(self.host)  # Run the base initializer

c = Logged("localhost", "db")
print(c.host, c.name)
#: localhost db
