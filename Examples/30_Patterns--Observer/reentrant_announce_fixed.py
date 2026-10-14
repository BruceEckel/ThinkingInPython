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
            print(f"unchanged: {new}")
            return  # Breaks the re-entry
        self._value = new
        self.announce(new)

model = TwoWay()

def echo(v: int) -> None:
    print(f"echo: {v}")
    model.value = v

model.connect(echo)
model.value = 1
#: echo: 1
#: unchanged: 1
