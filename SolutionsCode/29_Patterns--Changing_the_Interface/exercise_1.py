# exercise_1.py
from typing import Any
from exceptions import expected
from record import record

@record
class PairsAdapter:
    pairs: list[tuple[str, Any]]

    def __getitem__(self, key: str) -> Any:
        for k, v in self.pairs:
            if k == key:
                return v
        raise KeyError(key)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.pairs, name)

pairs = [("name", "Alice"), ("age", 30)]
adapter = PairsAdapter(pairs)
print(adapter["name"], adapter["age"])
#: Alice 30
# Reaches the list
adapter.append(("city", "Crested Butte"))
print(adapter["city"])
#: Crested Butte
print(len(pairs))  # The wrapped list itself grew
#: 3
with expected(KeyError):
    adapter["missing"]
#: [KeyError] 'missing'
with expected(TypeError):
    len(adapter)  # type: ignore
#: [TypeError] object of type 'PairsAdapter' has no len()
