# fetch_guarded.py
from newswire import Wire
from research import Feed, Unavailable, fetch
from stateless import (Effect, Need, catch, need, run,
                       supply, throw)

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

def edge(feed: Feed) -> str | Unavailable | Empty:
    guarded = catch(Unavailable, Empty)(fetch_nonempty)
    return run(supply(feed)(guarded)())

print(edge(Wire("markets close mixed")))
#: feed: fetching
#: markets close mixed
print(type(edge(Wire(""))).__name__)
#: feed: fetching
#: Empty
