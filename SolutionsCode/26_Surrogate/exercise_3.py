# exercise_3.py
from __future__ import annotations

class Box:
    def __init__(self, data: list) -> None:
        self.data = data
        self.owners = 1

class CowList:
    def __init__(self, data: list | None = None,
                 _box: Box | None = None) -> None:
        self._box = (
            _box if _box is not None else Box(list(data or [])))

    def share(self) -> CowList:
        self._box.owners += 1
        return CowList(_box=self._box)  # Shares the same Box, for now

    def append(self, item: object) -> None:
        if self._box.owners > 1:
            # Someone else shares this Box: copy before mutating
            self._box.owners -= 1
            self._box = Box(list(self._box.data))
        self._box.data.append(item)

    def __len__(self) -> int:
        return len(self._box.data)

    def __repr__(self) -> str:
        return repr(self._box.data)

a = CowList([1, 2, 3])
b = a.share()
print(a._box is b._box, a._box.owners)
#: True 2
b.append(4)
print(a, b)
#: [1, 2, 3] [1, 2, 3, 4]
print(a._box is b._box)
#: False
