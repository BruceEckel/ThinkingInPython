# cleanup.py
from typing import ClassVar

class Counter:
    # Number of objects of this class
    count: ClassVar[int] = 0

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "created")
        Counter.count += 1

    def __del__(self) -> None:
        Counter.count -= 1
        print(self.name, "deleted,", Counter.count, "left")

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))
#: First created
#: Second created
#: Third created

for c in counters:
    del c
print(Counter.count)
#: 3
print("End of delete loop")
#: End of delete loop
