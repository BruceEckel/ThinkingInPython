# catch_everything.py
from newswire import Library, Wire
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable, research)
from stateless import run, supply
from stateless.effect import catch_all

def outcome(
    feed: Feed, book: Encyclopedia
) -> str | Unavailable | NotInteresting | NoArticle:
    bound = supply(feed, book)(research)
    return run(catch_all(bound)())

dull = outcome(Wire("mild and cloudy"), Library({}))
#: feed: fetching
print(type(dull).__name__)
#: NotInteresting
missing = outcome(Wire("genome mapped"), Library({}))
#: feed: fetching
#: library: looking up genome
print(type(missing).__name__)
#: NoArticle
