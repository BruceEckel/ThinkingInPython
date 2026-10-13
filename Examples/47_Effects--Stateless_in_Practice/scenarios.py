# scenarios.py
from typing import assert_never
from newswire import EMPTY, SHELF, STOCKS, WEATHER, DeadWire
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

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(STOCKS, SHELF))  # [1]
#: feed: fetching
#: library: looking up stock market
#: a history
print(outcome(WEATHER, SHELF))  # [2]
#: feed: fetching
#: nothing worth researching
print(outcome(STOCKS, EMPTY))  # [3]
#: feed: fetching
#: library: looking up stock market
#: no article on that topic
print(outcome(DeadWire(), SHELF))  # [4]
#: no headline today
