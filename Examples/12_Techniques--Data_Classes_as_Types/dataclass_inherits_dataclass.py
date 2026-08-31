# dataclass_inherits_dataclass.py
from dataclasses import dataclass

@dataclass
class Connection:
    host: str

@dataclass
class Logged(Connection):
    name: str

c = Logged("localhost", "db")
print(c.host, c.name)
#: localhost db
