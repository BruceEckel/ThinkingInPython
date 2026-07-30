# clock.py
from datetime import datetime
from stateless import Ability, Depend

class Now(Ability[datetime]):
    pass

def now() -> Depend[Now, datetime]:
    moment: datetime = yield from Now()
    return moment
