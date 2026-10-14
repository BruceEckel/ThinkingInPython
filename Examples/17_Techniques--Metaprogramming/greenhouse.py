# greenhouse.py
from events import NAMES, EventMaker, make

class EventMakers(dict[str, EventMaker]):
    def __missing__(self, name: str) -> EventMaker:
        if name not in NAMES:
            raise KeyError(f"Unknown event class: {name!r}")
        print(f"Creating {name}")
        new_cls = make(name)
        self[name] = new_cls
        return new_cls

    def built(self) -> str:
        return (f"{len(self)} of {len(NAMES)}"
                " event classes built")
