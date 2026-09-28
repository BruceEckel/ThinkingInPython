# self_removing_responder.py
from broadcaster import Broadcaster

broadcaster = Broadcaster[object]()
seen: list[str] = []

def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    broadcaster.unsubscribe(once)

def always(data: object) -> None:
    seen.append(f"always: {data}")

broadcaster.subscribe(once)
broadcaster.subscribe(always)
broadcaster.announce(1)
broadcaster.announce(2)
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
