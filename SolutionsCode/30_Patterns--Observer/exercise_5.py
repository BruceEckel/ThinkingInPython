# exercise_5.py
from collections.abc import Callable
from result import Err, Ok, Result

type Listener[T] = Callable[[T], Result[None, str]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[Listener[T]] = []

    def subscribe(self, listener: Listener[T]) -> None:
        self._listeners.append(listener)

    def announce(self, data: T) -> list[Err[str]]:
        return [
            result
            for listener in list(self._listeners)
            if isinstance(result := listener(data), Err)
        ]

def succeeds[T](
    action: Callable[[T], None],
) -> Listener[T]:
    def listener(data: T) -> Result[None, str]:
        action(data)
        return Ok(None)
    return listener

def checked(data: int) -> Result[None, str]:
    if data < 0:
        return Err(f"cannot handle {data}")
    return Ok(None)

received: list[int] = []
source = Broadcaster[int]()
source.subscribe(checked)
source.subscribe(succeeds(received.append))
print(source.announce(7), received)
#: [] [7]
print(source.announce(-1), received)
#: [Err(error='cannot handle -1')] [7, -1]
