# parallel.py
import time
from concurrent.futures import Executor, ThreadPoolExecutor
from stateless import (
    Async,
    Depend,
    Need,
    Success,
    Task,
    as_type,
    fork,
    run,
    success,
    supply,
    wait,
)

@fork
def slow_square(n: int) -> Success[int]:
    time.sleep(0.05)
    return success(n * n)

def squares(
    count: int,
) -> Depend[Need[Executor] | Async, list[int]]:
    tasks: list[Task[int]] = []
    for n in range(count):
        task = yield from slow_square(n)
        tasks.append(task)
    results: list[int] = []
    for task in tasks:
        value = yield from wait(task)
        results.append(value)
    return results

with ThreadPoolExecutor(max_workers=5) as pool:
    start = time.perf_counter()
    out = run(supply(as_type(Executor)(pool))(squares)(5))
    elapsed = time.perf_counter() - start
print(out)
#: [0, 1, 4, 9, 16]
print(f"five 50ms tasks under 150ms: {elapsed < 0.15}")
#: five 50ms tasks under 150ms: True
