# Changing the Interface: Solutions

## 1. Adapting a 2D array into a dictionary interface

```python
# exercise_1.py
from typing import Any

class ArrayToDictAdapter:
    "Adapts a 2D array of [key, value] rows to a dict-like interface."
    def __init__(self, rows: list[list[Any]]) -> None:
        self._data = {row[0]: row[1] for row in rows}

    def __getitem__(self, key: Any) -> Any:
        return self._data[key]

    def __contains__(self, key: Any) -> bool:
        return key in self._data

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

rows = [["name", "Alice"], ["age", 30], ["city", "Crested Butte"]]
adapted = ArrayToDictAdapter(rows)
print(adapted["name"], adapted["age"])
#: Alice 30
print("city" in adapted)
#: True
print(dict(adapted.items()))
#: {'name': 'Alice', 'age': 30, 'city': 'Crested Butte'}
```

`WhatIHave` here is a 2D array (a `list` of `[key, value]` rows), and
`WhatIWant` is the small piece of `dict`'s interface most code actually
needs: `[key]`, `in`, `keys()`, and `items()`. The adapter builds a
real `dict` once, in `__init__()`, from the array's rows, and every
other method simply delegates to that `dict`. Because the conversion
happens up front rather than on every access, later lookups are the
same O(1) dictionary lookups a real `dict` would give you, not a
linear scan of the original array repeated on every `[key]`.

A Python built-in already covers the common case directly:
`dict(rows)` performs the same conversion when each row is a
two-element `[key, value]` pair, with no adapter class at all. Writing
`ArrayToDictAdapter` earns its place only when the wrapped object must
keep behaving like the original array in some other context too (so
it cannot simply be replaced by a plain `dict`), or when the adapter
needs to add behavior beyond what a plain conversion gives you, such
as lazily building the dictionary on first access instead of eagerly
in `__init__()`.
