# task_scaling.py
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Final

TOTAL: Final[int] = 20_000_000  # Loop iterations, split across tasks
CORE_MULTIPLIER: Final[int] = 2  # Largest sweep point = cores * this

def work_chunk(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i  # CPU-intensive
    return total

def timed_split(
    pool: ProcessPoolExecutor, total_work: int, tasks: int
) -> float:
    chunk = total_work // tasks
    start = time.perf_counter()
    list(pool.map(work_chunk, [chunk] * tasks))
    return time.perf_counter() - start

if __name__ == "__main__":
    cores = os.cpu_count() or 1
    max_tasks = cores * CORE_MULTIPLIER
    doubled = {2**i for i in range(20) if 2**i <= max_tasks}
    task_counts = sorted(doubled | {cores, max_tasks})
    print(f"cores = {cores}, total = {TOTAL}")

    with ProcessPoolExecutor() as pool:
        list(pool.map(work_chunk, [1]))  # Warm up, not timed
        baseline: float | None = None
        for tasks in task_counts:
            elapsed = timed_split(pool, TOTAL, tasks)
            baseline = baseline or elapsed
            print(
                f"{tasks:>3} tasks: {elapsed:6.3f}s "
                f"({baseline / elapsed:4.2f}x)"
            )
