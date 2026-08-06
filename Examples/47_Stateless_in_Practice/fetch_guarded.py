# fetch_guarded.py
from dataclasses import dataclass
from research import Feed, Unavailable, fetch
from stateless import Effect, Need, catch, need, run, supply, throw

class Empty(Exception):
    pass

def fetch_nonempty() -> Effect[
    Need[Feed], Unavailable | Empty, str
]:
    feed = yield from need(Feed)
    headline = yield from fetch(feed)
    if not headline:
        yield from throw(Empty())
    return headline

@dataclass
class Ticker:
    headline: str
    def latest(self) -> str:
        return self.headline

def edge(feed: Feed) -> str | Unavailable | Empty:
    guarded = catch(Unavailable, Empty)(fetch_nonempty)
    return run(supply(feed)(guarded)())

print(edge(Ticker("markets close mixed")))
#: markets close mixed
print(type(edge(Ticker(""))).__name__)
#: Empty
