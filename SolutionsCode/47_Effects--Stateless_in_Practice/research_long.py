# research_long.py
from research import (
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
    fetch,
    look_up,
    topic_of,
)
from stateless import Effect, Need, need, throws

class TooLong(Exception):
    pass

LIMIT: int = 100

@throws(TooLong)
def within_limit(article: str) -> str:
    if len(article) > LIMIT:
        raise TooLong(f"{len(article)} characters")
    return article

def research() -> Effect[
    Need[Feed] | Need[Encyclopedia],
    Unavailable | NotInteresting | NoArticle | TooLong,
    str,
]:
    feed = yield from need(Feed)
    headline = yield from fetch(feed)
    topic = yield from topic_of(headline)
    book = yield from need(Encyclopedia)
    article = yield from look_up(book, topic)
    checked = yield from within_limit(article)
    return checked
