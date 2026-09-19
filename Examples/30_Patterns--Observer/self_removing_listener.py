# self_removing_listener.py
from broadcaster import Broadcaster

source = Broadcaster[object]()
seen: list[str] = []

def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    source.unsubscribe(once)

def always(data: object) -> None:
    seen.append(f"always: {data}")

source.subscribe(once)
source.subscribe(always)
source.announce(1)
source.announce(2)
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
