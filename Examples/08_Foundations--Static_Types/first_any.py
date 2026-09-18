# first_any.py
from typing import Any
from exceptions import expected

def first_any(items: list) -> Any:
    return items[0]

n = first_any([10, 20, 30])
with expected(AttributeError):
    n.nonexistent_method()
#: [AttributeError] 'int' object has no attribute
#: 'nonexistent_method'
