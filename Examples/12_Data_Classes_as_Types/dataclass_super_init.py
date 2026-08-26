# dataclass_super_init.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.url = f"tcp://{host}:5432"

@dataclass
class Logged(Connection):
    host: str
    name: str

    def __post_init__(self) -> None:
        # Run the base initializer
        super().__init__(self.host)

c = Logged("localhost", "db")
print(c.url, c.name)
#: tcp://localhost:5432 db
