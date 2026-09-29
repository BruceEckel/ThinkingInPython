# fixed_broadcaster.py
from broadcaster import Responder
from record import record

@record
class FixedBroadcaster[T]:
    responders: tuple[Responder[T], ...]

    def announce(self, data: T) -> None:
        for responder in self.responders:
            responder(data)

log: list[float] = []
broadcaster = FixedBroadcaster[float]((
    log.append,
    lambda c: print("alarm!" if c > 100 else "ok"),
))
broadcaster.announce(25.0)
#: ok
broadcaster.announce(150.0)
#: alarm!
print(log)
#: [25.0, 150.0]
