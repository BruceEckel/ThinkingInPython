# exercise_6.py
from feeds import SHELF, StaleWire
from report import report
from research import Encyclopedia, Feed
from stateless import run, supply

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(StaleWire(), SHELF))
#: feed: fetching
#: no headline today
