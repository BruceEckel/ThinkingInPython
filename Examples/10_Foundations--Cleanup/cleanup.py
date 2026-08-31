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
        print(self.name, "deleted")
        Counter.count -= 1
        if Counter.count == 0:
            print("Last Counter object deleted")
        else:
            print(Counter.count,
                  "Counter objects remaining")

    def __repr__(self) -> str:
        return f"Counter({self.name!r} {self.count})"

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))
#: First created
#: Second created
#: Third created

for c in counters:
    print(c)
    del c
#: Counter('First' 3)
#: Counter('Second' 3)
#: Counter('Third' 3)
print("End of delete loop")
#: End of delete loop
