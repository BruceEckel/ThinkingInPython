# factory_checking.py
from dataclasses import dataclass, field

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
try:
    Unchecked().data["theme"] = "dark"
except TypeError as e:
    print(e)
#: 'set' object does not support item assignment
print(Checked().data)
#: {}
