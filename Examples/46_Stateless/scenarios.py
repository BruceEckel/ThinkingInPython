# scenarios.py
from dataclasses import dataclass
from typing import Final
from research import (
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
    research,
)
from stateless import Depend, Need, catch, run, supply

@dataclass
class Wire:
    headline: str
    def latest(self) -> str:
        print("feed: fetching")
        return self.headline

class DeadWire:
    def latest(self) -> str:
        raise Unavailable("offline")

@dataclass
class Library:
    articles: dict[str, str]
    def article(self, topic: str) -> str:
        print(f"library: looking up {topic}")
        if topic not in self.articles:
            raise NoArticle(topic)
        return self.articles[topic]

def report() -> Depend[Need[Feed] | Need[Encyclopedia], str]:
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
        case _:
            return found

STOCKS: Final[Wire] = Wire("stock market rising")
WEATHER: Final[Wire] = Wire("mild and cloudy")
SHELF: Final[Library] = Library({"stock market": "a history"})
EMPTY: Final[Library] = Library({})

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(STOCKS, SHELF))
print(outcome(WEATHER, SHELF))
print(outcome(STOCKS, EMPTY))
print(outcome(DeadWire(), SHELF))
#: feed: fetching
#: library: looking up stock market
#: a history
#: feed: fetching
#: nothing worth researching
#: feed: fetching
#: library: looking up stock market
#: no article on that topic
#: no headline today
