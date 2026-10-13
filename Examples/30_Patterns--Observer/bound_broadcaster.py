# bound_broadcaster.py
from broadcaster import Responder
from record import record

@record
class BoundBroadcaster[T]:
    responders: tuple[Responder[T], ...]

    def announce(self, data: T) -> None:
        for responder in self.responders:
            responder(data)

log: list[float] = []
broadcaster = BoundBroadcaster[float]((
    log.append,
    lambda c: print(f"alarm: {c > 100}"),
))
broadcaster.announce(25.0)
#: alarm: False
broadcaster.announce(150.0)
#: alarm: True
print(log)
#: [25.0, 150.0]
