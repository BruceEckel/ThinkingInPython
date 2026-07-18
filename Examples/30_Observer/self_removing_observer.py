# self_removing_observer.py
from observers import Observable

obs = Observable()
seen: list[str] = []

def once(data: object) -> None:
    seen.append(f"once: {data}")
    obs.unsubscribe(once)  # Detaches itself mid-notification

obs.subscribe(once)
obs.subscribe(lambda d: seen.append(f"always: {d}"))
obs.notify(1)
obs.notify(2)
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
