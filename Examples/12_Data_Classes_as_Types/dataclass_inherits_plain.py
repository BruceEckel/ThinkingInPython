# dataclass_inherits_plain.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.url = f"tcp://{host}:5432"

@dataclass
class Logged(Connection):
    name: str

c = Logged("db")
print(c.name)
#: db
# Connection.__init__ never ran, so 'host' and 'url' were never set:
print(hasattr(c, "host"), hasattr(c, "url"))
#: False False
