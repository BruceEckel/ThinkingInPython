# weak_pool.py
from dataclasses import dataclass
from typing import Final
from weakref import WeakValueDictionary

@dataclass(frozen=True)
class Name:
    text: str

_pool: Final[WeakValueDictionary[str, Name]] = (
    WeakValueDictionary())

def name(text: str) -> Name:
    found: Name | None = _pool.get(text)
    if found is None:
        found = Name(text)
        _pool[text] = found
    return found

if __name__ == "__main__":
    alpha = name("alpha")
    alias = name("alpha")
    print(alpha is alias, len(_pool))
    del alpha, alias
    print(len(_pool))
#: True 1
#: 0
