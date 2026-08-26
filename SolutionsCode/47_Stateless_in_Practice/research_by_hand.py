# research_by_hand.py
from feeds import Library, Wire
from research import (
    TOPICS,
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
)
from research_long import LIMIT, TooLong

def topic_of(headline: str) -> str:
    for candidate in TOPICS:
        if candidate in headline:
            return candidate
    raise NotInteresting(headline)

def within_limit(article: str) -> str:
    if len(article) > LIMIT:
        raise TooLong(f"{len(article)} characters")
    return article

def research_and_report(
    feed: Feed, book: Encyclopedia
) -> str:
    try:
        headline = feed.latest()
    except Unavailable:
        return "no headline today"
    try:
        topic = topic_of(headline)
    except NotInteresting:
        return "nothing worth researching"
    try:
        return within_limit(book.article(topic))
    except NoArticle:
        return "no article on that topic"
    except TooLong:
        return "article too long"

print(research_and_report(
    Wire("genome mapped"),
    Library({"genome": "short enough"})))
#: feed: fetching
#: library: looking up genome
#: short enough
