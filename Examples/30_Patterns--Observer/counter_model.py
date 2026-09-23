# counter_model.py
from broadcaster import Broadcaster

class Counter(Broadcaster[int]):
    def __init__(self) -> None:
        super().__init__()
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def add(self, delta: int) -> None:
        self._count += delta
        self.announce(self._count)
