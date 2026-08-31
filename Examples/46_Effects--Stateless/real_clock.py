# real_clock.py
import time
from sleep_effect import delayed_sum
from stateless import run, supply
from stateless.time import Time

start = time.perf_counter()
result = run(supply(Time())(delayed_sum)([1, 2, 3]))
elapsed = time.perf_counter() - start
print(result)
#: 6
print(f"{elapsed >= 0.03 = }")
#: elapsed >= 0.03 = True
