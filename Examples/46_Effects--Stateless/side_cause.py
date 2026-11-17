# side_cause.py
import random
from stateless import Depend, Need, need, run, supply

def roll() -> Depend[Need[random.Random], int]:
    rng = yield from need(random.Random)
    return rng.randint(1, 6)

bound = supply(random.Random(47))(roll)
print(run(bound()), run(bound()))
#: 3 1
