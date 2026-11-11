# factory_checking.py
from dataclasses import dataclass, field
from exceptions import expected

@dataclass
class Mismatched:
    # A set
    data: dict[str, str] = field(default_factory=set)  # type: ignore

print(type(Mismatched().data).__name__)
#: set
with expected(TypeError):
    Mismatched().data["theme"] = "dark"
#: [TypeError] 'set' object does not support item assignment
