# dataclass_inherits_dataclass.py
from dataclasses import dataclass

@dataclass
class Connection:
    host: str

@dataclass
class NamedConnection(Connection):
    name: str

c = NamedConnection("localhost", "db")
print(c.host, c.name)
#: localhost db
