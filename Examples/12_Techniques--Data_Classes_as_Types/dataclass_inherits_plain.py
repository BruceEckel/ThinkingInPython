# dataclass_inherits_plain.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.url = f"tcp://{host}:5432"

@dataclass
class NamedConnection(Connection):
    name: str

c = NamedConnection("db")
print(c.name)
#: db
# Connection.__init__ never ran, so host and url are unset:
print(hasattr(c, "host"), hasattr(c, "url"))
#: False False
