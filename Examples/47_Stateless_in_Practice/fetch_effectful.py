# fetch_effectful.py
from research import Feed, Unavailable
from stateless import Depend, Need, need, throws

@throws(Unavailable)
def fetch_headline() -> Depend[Need[Feed], str]:
    feed = yield from need(Feed)
    return feed.latest()
