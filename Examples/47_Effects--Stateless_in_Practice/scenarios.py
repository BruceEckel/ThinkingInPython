# scenarios.py
from typing import Final, assert_never
from newswire import DeadWire, Library, Wire
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable, research)
from stateless import Depend, Need, catch, run, supply

def report() -> Depend[
    Need[Feed] | Need[Encyclopedia], str
]:
    caught = catch(Unavailable, NotInteresting, NoArticle)
    found: str | Unavailable | NotInteresting | NoArticle
    found = yield from caught(research)()
    match found:
        case Unavailable():
            return "no headline today"
        case NotInteresting():
            return "nothing worth researching"
        case NoArticle():
            return "no article on that topic"
        case str():
            return found
        case _:
            assert_never(found)

STOCKS: Final[Wire] = Wire("stock market rising")
WEATHER: Final[Wire] = Wire("mild and cloudy")
SHELF: Final[Library] = Library(
    {"stock market": "a history"})
EMPTY: Final[Library] = Library({})

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(STOCKS, SHELF))
#: feed: fetching
#: library: looking up stock market
#: a history
print(outcome(WEATHER, SHELF))
#: feed: fetching
#: nothing worth researching
print(outcome(STOCKS, EMPTY))
#: feed: fetching
#: library: looking up stock market
#: no article on that topic
print(outcome(DeadWire(), SHELF))
#: no headline today
