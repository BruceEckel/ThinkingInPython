# self_removing_responder.py
from broadcaster import Broadcaster

broadcaster = Broadcaster[object]()
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
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
