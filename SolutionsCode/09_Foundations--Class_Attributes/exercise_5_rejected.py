# exercise_5_rejected.py
from dataclasses import dataclass
from exceptions import ignore

with ignore(ValueError):
    @dataclass
    class Cart:
        items: list[str] = []
#: [ValueError] mutable default <class 'list'> for field
#: items is not allowed: use default_factory
