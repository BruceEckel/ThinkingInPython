# yield_from_list.py
from collections.abc import Iterator

def relay() -> Iterator[int | None]:
    v: None = yield from [1, 2, 3]
    yield v

print(list(relay()))
#: [1, 2, 3, None]
