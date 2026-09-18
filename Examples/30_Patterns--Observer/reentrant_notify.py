# reentrant_notify.py
from exceptions import expected
from observers import Observable

class TwoWay(Observable[int]):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new: int) -> None:
        self._value = new
        self.notify(new)  # Re-enters if written back

model = TwoWay()
model.subscribe(
    lambda v: setattr(model, "value", v))
with expected(RecursionError):
    model.value = 1
#: [RecursionError] maximum recursion depth exceeded
