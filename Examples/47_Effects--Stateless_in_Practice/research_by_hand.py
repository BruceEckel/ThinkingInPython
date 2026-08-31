# research_by_hand.py
from research import (
    TOPICS,
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
)

def topic_of(headline: str) -> str:
    for candidate in TOPICS:
        if candidate in headline:
            return candidate
    raise NotInteresting(headline)

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
        return book.article(topic)
    except NoArticle:
        return "no article on that topic"
