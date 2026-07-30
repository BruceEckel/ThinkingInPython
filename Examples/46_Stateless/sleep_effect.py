# sleep_effect.py
import time
from stateless import Async, Depend, Need, run, supply
from stateless.time import Time, sleep

def delayed_sum(
    values: list[int],
) -> Depend[Need[Time] | Async, int]:
    total = 0
    for value in values:
        yield from sleep(0.01)
        total += value
    return total

start = time.perf_counter()
result = run(supply(Time())(delayed_sum)([1, 2, 3]))
elapsed = time.perf_counter() - start
print(result)
#: 6
print(f"waited 30ms or more: {elapsed >= 0.03}")
#: waited 30ms or more: True
