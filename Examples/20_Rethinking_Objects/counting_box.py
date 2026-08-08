# counting_box.py
from dataclasses import dataclass, field

@dataclass
class CountingBox:
    items: list[int] = field(default_factory=list)
    appends: int = 0

    def append(self, item: int) -> None:
        self.appends += 1
        self.items.append(item)

    def extend(self, more: list[int]) -> None:
        for item in more:
            self.append(item)

box = CountingBox()
box.append(1)
box.extend([2, 3])
print(len(box.items), box.appends)
#: 3 3
