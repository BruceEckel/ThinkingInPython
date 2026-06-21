# cleanup.py
from typing import ClassVar


class Counter:
    count: ClassVar[int] = 0   # Number of objects of this class

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, 'created')
        Counter.count += 1

    def __del__(self) -> None:
        print(self.name, 'deleted')
        Counter.count -= 1
        if Counter.count == 0:
            print('Last Counter object deleted')
        else:
            print(Counter.count, 'Counter objects remaining')

    def __repr__(self) -> str:
        return f"Counter({self.name!r} {self.count})"

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))

for c in counters:
    print(c)
    del c
print("End of delete loop")
