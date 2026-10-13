# self_removing_responder.py
from typing import override
from broadcaster import Broadcaster

class Skipping(Broadcaster[object]):
    @override
    def announce(self, data: object) -> None:
        for responder in self._responders:  # No copy
            responder(data)

def trace(broadcaster: Broadcaster[object]) -> list[str]:
    seen: list[str] = []

    def once(data: object) -> None:
        seen.append(f"once: {data}")
        # Disconnects mid-notification
        broadcaster.disconnect(once)

    def always(data: object) -> None:
        seen.append(f"always: {data}")

    broadcaster.connect(once)
    broadcaster.connect(always)
    broadcaster.announce(1)
    broadcaster.announce(2)
    return seen

print(trace(Broadcaster[object]()))
#: ['once: 1', 'always: 1', 'always: 2']
print(trace(Skipping()))
#: ['once: 1', 'always: 2']
