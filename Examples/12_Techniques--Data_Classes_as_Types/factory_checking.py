# factory_checking.py
from dataclasses import dataclass, field
from exceptions import expected

@dataclass
class Unchecked:
    # A set
    data: dict[str, str] = field(default_factory=set)

@dataclass
class Checked:
    data: dict[str, str] = field(
        default_factory=dict[str, str])

print(type(Unchecked().data).__name__)
#: set
with expected(TypeError):
    Unchecked().data["theme"] = "dark"
#: [TypeError] 'set' object does not support item assignment
print(Checked().data)
#: {}
