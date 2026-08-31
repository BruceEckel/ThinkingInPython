# exercise_6.py
from feeds import SHELF, DullWire
from report import report
from research import Encyclopedia, Feed
from stateless import run, supply

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(DullWire(), SHELF))
#: feed: fetching
#: nothing worth researching
