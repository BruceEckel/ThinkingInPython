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
