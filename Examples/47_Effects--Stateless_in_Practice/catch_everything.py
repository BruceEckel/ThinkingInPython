# catch_everything.py
from newswire import EMPTY, SHELF, STOCKS, WEATHER
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable, research)
from stateless import run, supply
from stateless.effect import catch_all

def outcome(
    feed: Feed, book: Encyclopedia
) -> str | Unavailable | NotInteresting | NoArticle:
    bound = supply(feed, book)(research)
    return run(catch_all(bound)())

dull = outcome(WEATHER, SHELF)
#: feed: fetching
print(type(dull).__name__)
#: NotInteresting
missing = outcome(STOCKS, EMPTY)
#: feed: fetching
#: library: looking up stock market
print(type(missing).__name__)
#: NoArticle
