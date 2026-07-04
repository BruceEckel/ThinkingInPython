# weak_pool.py
from dataclasses import dataclass
from typing import Final
from weakref import WeakValueDictionary

@dataclass(frozen=True)
class Symbol:
    name: str

_pool: Final[WeakValueDictionary[str, Symbol]] = (
    WeakValueDictionary())

def symbol(name: str) -> Symbol:
    found = _pool.get(name)
    if found is None:
        found = Symbol(name)
        _pool[name] = found
    return found

if __name__ == "__main__":
    alpha = symbol("alpha")
    alias = symbol("alpha")
    print(alpha is alias, len(_pool))
    del alpha, alias
    print(len(_pool))
#: True 1
#: 0
