# exercise_4.py
from typing import ClassVar

class Counter:
    count: ClassVar[int] = 0

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "created")
        Counter.count += 1

    def __del__(self) -> None:
        print(self.name, "deleted")
        Counter.count -= 1

    def __repr__(self) -> str:
        return f"Counter({self.name!r} {self.count})"

counters = [Counter(name) for name in ["First", "Second", "Third"]]

for c in counters:
    print(c)
    del c
print("End of delete loop")
#: First created
#: Second created
#: Third created
#: Counter('First' 3)
#: Counter('Second' 3)
#: Counter('Third' 3)
#: End of delete loop
