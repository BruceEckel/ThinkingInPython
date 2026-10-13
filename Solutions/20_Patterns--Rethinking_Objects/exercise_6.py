# exercise_6.py
from typing import Final, Protocol

class Cache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...

class NullCache:
    def get(self, key: str) -> str | None:
        return None

    def set(self, key: str, value: str) -> None:
        pass

NO_CACHE: Final[NullCache] = NullCache()

def render(key: str, cache: Cache = NO_CACHE) -> str:
    cached = cache.get(key)
    if cached is not None:  # A miss is information
        return cached
    page = f"<p>{key}</p>"
    cache.set(key, page)
    return page

NO_CACHE.set("a", "apple")
print(NO_CACHE.get("a"))
#: None
print(render("home"))
#: <p>home</p>
