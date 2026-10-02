# exercise_10.py
from dataclasses import dataclass
from stateless import (Effect, Need, catch, need, run,
                       supply, throw, throws)

class Unavailable(Exception):
    pass

class Empty(Exception):
    pass

@dataclass
class Ticker:
    headline: str
    def latest(self) -> str:
        return self.headline

@throws(Unavailable)
def fetch(feed: Ticker) -> str:
    return feed.latest()

def thrown() -> Effect[
    Need[Ticker], Unavailable | Empty, str
]:
    feed = yield from need(Ticker)
    headline = yield from fetch(feed)
    if not headline:
        yield from throw(Empty())
    return headline

@throws(Empty)
def lifted() -> Effect[Need[Ticker], Unavailable, str]:
    feed = yield from need(Ticker)
    headline = yield from fetch(feed)
    if not headline:
        raise Empty()
    return headline

for version in (thrown, lifted):
    guarded = catch(Unavailable, Empty)(version)
    for feed in (Ticker("markets close mixed"), Ticker("")):
        result = run(supply(feed)(guarded)())
        print(f"{version.__name__}: {result!r}")
#: thrown: 'markets close mixed'
#: thrown: Empty()
#: lifted: 'markets close mixed'
#: lifted: Empty()
