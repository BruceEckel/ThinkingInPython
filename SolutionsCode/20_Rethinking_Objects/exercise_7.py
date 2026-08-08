# exercise_7.py
from dataclasses import dataclass, field
from typing import override

class CountingList(list[int]):
    def __init__(self) -> None:
        super().__init__()
        self.appends = 0
        self.sets = 0

    @override
    def append(self, item: int, /) -> None:
        self.appends += 1
        super().append(item)

    @override
    def __setitem__(self, index, value) -> None:
        self.sets += 1
        super().__setitem__(index, value)

counted = CountingList()
counted.append(1)
counted.extend([2, 3])  # Past append()
counted[0] = 99  # Counted
counted.insert(0, 7)  # Past both overrides
print(len(counted), counted.appends, counted.sets)
#: 4 1 1

@dataclass
class CountingBox:
    items: list[int] = field(default_factory=list)
    appends: int = 0
    sets: int = 0

    def append(self, item: int) -> None:
        self.appends += 1
        self.items.append(item)

    def extend(self, more: list[int]) -> None:
        for item in more:
            self.append(item)

    def __setitem__(self, index: int, value: int) -> None:
        self.sets += 1
        self.items[index] = value

box = CountingBox()
box.append(1)
box.extend([2, 3])
box[0] = 99
print(len(box.items), box.appends, box.sets)
#: 3 3 1
