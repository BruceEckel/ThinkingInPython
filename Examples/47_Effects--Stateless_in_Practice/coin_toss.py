# coin_toss.py
import random
from stateless import Ability, Depend, handle, run

class Flip(Ability[bool]):
    pass

def flip() -> Depend[Flip, bool]:
    result: bool = yield from Flip()
    return result

def count_heads(tosses: int) -> Depend[Flip, int]:
    heads = 0
    for _ in range(tosses):
        if (yield from flip()):
            heads += 1
    return heads

script = iter((True, False, True, True, False))

def scripted(request: Flip) -> bool:
    return next(script)

def coin(request: Flip) -> bool:
    return random.random() < 0.5

print(run(handle(scripted)(count_heads)(5)))
#: 3
heads = run(handle(coin)(count_heads)(10_000))
print(4_000 < heads < 6_000)
#: True
