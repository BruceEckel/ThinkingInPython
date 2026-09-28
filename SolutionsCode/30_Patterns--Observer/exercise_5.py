# exercise_5.py
from collections.abc import Callable
from result import Err, Ok, Result

type Responder[T] = Callable[[T], Result[None, str]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def subscribe(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> list[Err[str]]:
        return [
            result
            for responder in list(self._responders)
            if isinstance(result := responder(data), Err)
        ]

def succeeds[T](
    action: Callable[[T], None],
) -> Responder[T]:
    def responder(data: T) -> Result[None, str]:
        action(data)
        return Ok(None)
    return responder

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
