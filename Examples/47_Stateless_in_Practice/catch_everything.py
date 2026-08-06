# catch_everything.py
from dataclasses import dataclass
from research import (
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
    research,
)
from stateless import run, supply
from stateless.effect import catch_all

@dataclass
class Bulletin:
    headline: str
    def latest(self) -> str:
        return self.headline

class BareShelf:
    def article(self, topic: str) -> str:
        raise NoArticle(topic)

def outcome(
    feed: Feed, book: Encyclopedia
) -> str | Unavailable | NotInteresting | NoArticle:
    bound = supply(feed, book)(research)
    return run(catch_all(bound)())

dull = outcome(Bulletin("mild and cloudy"), BareShelf())
print(type(dull).__name__)
#: NotInteresting
missing = outcome(Bulletin("genome mapped"), BareShelf())
print(type(missing).__name__)
#: NoArticle
