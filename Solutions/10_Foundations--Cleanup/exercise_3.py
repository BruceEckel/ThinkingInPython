# exercise_3.py
from typing import ClassVar

class Counter:
    count: ClassVar[int] = 0

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "created")
        Counter.count += 1

    def __del__(self) -> None:
        Counter.count -= 1
        print(self.name, "deleted,", Counter.count, "left")

counters = [Counter(name)
            for name in ["First", "Second", "Third"]]
#: First created
#: Second created
#: Third created

for c in counters:
    del c
print(Counter.count)
#: 3
print("End of delete loop")
#: End of delete loop
