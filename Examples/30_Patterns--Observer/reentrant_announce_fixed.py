# reentrant_announce_fixed.py
from broadcaster import Broadcaster

class TwoWay(Broadcaster[int]):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new: int) -> None:
        if new == self._value:
            return  # Breaks the re-entry
        self._value = new
        self.announce(new)

model = TwoWay()
seen: list[int] = []

def echo(v: int) -> None:
    seen.append(v)
    model.value = v  # Now a no-op

model.subscribe(echo)
model.value = 1
print(seen)
#: [1]
