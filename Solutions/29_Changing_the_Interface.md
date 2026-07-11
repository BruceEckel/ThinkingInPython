# Changing the Interface: Solutions

## 1. A dict-style lookup over a list of pairs

```python
# exercise_1.py
from typing import Any

class PairsAdapter:
    "Gives a list of (key, value) pairs a dict-style lookup."
    def __init__(self, pairs: list[tuple[str, Any]]) -> None:
        self._pairs = pairs

    def __getitem__(self, key: str) -> Any:
        for k, v in self._pairs:
            if k == key:
                return v
        raise KeyError(key)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._pairs, name)

pairs = [("name", "Alice"), ("age", 30)]
adapter = PairsAdapter(pairs)
print(adapter["name"], adapter["age"])
#: Alice 30
adapter.append(("city", "Crested Butte"))  # Reaches the list
print(adapter["city"])
#: Crested Butte
print(len(pairs))  # The wrapped list itself grew
#: 3
try:
    adapter["missing"]
except KeyError as e:
    print("KeyError:", e)
#: KeyError: 'missing'
```

The adapter adds the one method the caller wants, `__getitem__()`,
and forwards everything else to the wrapped list through
`__getattr__()`, the same shape as `getattr_adapter.py`.
`append()` is not defined on the adapter, so the lookup falls
through to the list, and the growth shows both through the adapter
and through the original name.
The lookup is a linear scan.
If the pairs are many and the lookups frequent, convert to a real
`dict` once (`dict(pairs)` does it) and adapt only when the object
must keep being a list to someone else.
