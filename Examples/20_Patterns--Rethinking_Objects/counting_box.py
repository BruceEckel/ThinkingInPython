# counting_box.py
from dataclasses import dataclass, field

@dataclass
class CountingBox:
    _items: list[int] = field(default_factory=list)
    appends: int = 0

    def __len__(self) -> int:
        return len(self._items)

    def append(self, item: int) -> None:
        self.appends += 1
        self._items.append(item)

    def extend(self, more: list[int]) -> None:
        for item in more:
            self.append(item)

box = CountingBox()
box.append(1)
box.extend([2, 3])
print(f"{len(box)=}, {box.appends=}")
#: len(box)=3, box.appends=3
