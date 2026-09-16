# first_any.py
from typing import Any
from exceptions import ignore

def first_any(items: list) -> Any:
    return items[0]

n = first_any([10, 20, 30])
with ignore(AttributeError):
    n.nonexistent_method()
#: AttributeError("'int' object has no attribute
#: 'nonexistent_method'")
