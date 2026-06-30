# dataclass_inherits_plain.py
from dataclasses import dataclass

class Connection:
    def __init__(self) -> None:
        self.open = True   # Setup the subclass relies on

@dataclass
class Logged(Connection):
    name: str

c = Logged("db")
print(c.name)
#: db
# Connection.__init__ never ran, so 'open' was never set:
print(hasattr(c, "open"))
#: False
