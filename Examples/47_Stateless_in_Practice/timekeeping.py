# timekeeping.py
from datetime import datetime, timedelta
from stateless import Ability, Depend

class Now(Ability[datetime]):
    pass

def now() -> Depend[Now, datetime]:
    moment: datetime = yield from Now()
    return moment

def stamp(message: str) -> Depend[Now, str]:
    moment = yield from now()
    return f"[{moment:%Y-%m-%d %H:%M}] {message}"

def batch_due(last_run: datetime) -> Depend[Now, bool]:
    moment = yield from now()
    return moment - last_run >= timedelta(hours=24)
