# counting_list.py
from typing import override

class CountingList(list[int]):
    def __init__(self) -> None:
        super().__init__()
        self.appends = 0

    @override
    def append(self, item: int, /) -> None:
        self.appends += 1
        super().append(item)

counted = CountingList()
counted.append(1)
counted.extend([2, 3])
print(len(counted), counted.appends)
#: 3 1
