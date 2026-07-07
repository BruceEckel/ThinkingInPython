# task_scaling.py
"""Split a fixed workload across a growing number of tasks and
time each split on a warm pool.

    python task_scaling.py
    python task_scaling.py --total 200_000_000 --max-tasks 128
"""
import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor

def work_chunk(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total

def timed_split(
    pool: ProcessPoolExecutor, total_work: int, tasks: int
) -> float:
    chunk = total_work // tasks
    start = time.perf_counter()
    list(pool.map(work_chunk, [chunk] * tasks))
    return time.perf_counter() - start

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--total", type=int, default=10_000_000,
        help="total loop iterations, split across tasks",
    )
    parser.add_argument(
        "--max-tasks", type=int, default=None,
        help="largest task count to try (default: 2 * cores)",
    )
    args = parser.parse_args()

    cores = os.cpu_count() or 1
    max_tasks = args.max_tasks or cores * 2
    task_counts = sorted({1, 2, cores, max_tasks})
    print(f"cores = {cores}, total = {args.total}")

    with ProcessPoolExecutor() as pool:
        list(pool.map(work_chunk, [1]))  # Warm up, not timed
        baseline = None
        for tasks in task_counts:
            elapsed = timed_split(pool, args.total, tasks)
            baseline = baseline or elapsed
            print(
                f"{tasks:>3} tasks: {elapsed:6.3f}s "
                f"({baseline / elapsed:4.2f}x)"
            )

if __name__ == "__main__":
    main()
