# dataclass_inherits_plain.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host

@dataclass
class Logged(Connection):
    name: str

c = Logged("db")
print(c.name)
#: db
# Connection.__init__ never ran, so 'host' was never set:
print(hasattr(c, "host"))
#: False
