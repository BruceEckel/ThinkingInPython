# exercise_7.py
from datetime import timedelta
from feeds import SHELF, WEATHER
from research import Encyclopedia, Feed, research
from stateless import catch, retry, run, supply
from stateless.functions import RetryError
from stateless.schedule import recurs, spaced
from stateless.time import Time

THREE = recurs(3, spaced(timedelta(milliseconds=1)))

def attempt(feed: Feed, book: Encyclopedia) -> str | RetryError:
    retried = retry(THREE)(research)  # Named, so ty follows it
    caught = catch(RetryError)(retried)
    return run(supply(feed, book, Time())(caught)())

outcome = attempt(WEATHER, SHELF)
#: feed: fetching
#: feed: fetching
#: feed: fetching
print(type(outcome).__name__)
#: RetryError
if isinstance(outcome, RetryError):
    for failure in outcome.args[0]:
        print(f"  {type(failure).__name__}: {failure}")
#:   NotInteresting: mild and cloudy
#:   NotInteresting: mild and cloudy
#:   NotInteresting: mild and cloudy
