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
