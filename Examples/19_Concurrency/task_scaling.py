# task_scaling.py
"""
Split a fixed workload across a growing number of
tasks and time each split on a warm pool.

    python task_scaling.py
    python task_scaling.py --total 200_000_000 --max-tasks 128
    python task_scaling.py --auto
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

def plot_speedups(results: list[tuple[int, float]]) -> None:
    width = 40
    best = max(speedup for _, speedup in results)
    print("\nspeedup by task count:")
    for tasks, speedup in results:
        bar = "#" * max(1, round(speedup / best * width))
        print(f"{tasks:>4} | {bar:<{width}} {speedup:4.2f}x")

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--total", type=int, default=None,
        help="total loop iterations (default: 10_000_000, "
             "200_000_000 with --auto)",
    )
    parser.add_argument(
        "--max-tasks", type=int, default=None,
        help="largest task count to try (default: 2 * cores)",
    )
    parser.add_argument(
        "--auto", action="store_true",
        help="sweep task counts by doubling and plot the curve",
    )
    args = parser.parse_args()

    total = args.total or (200_000_000 if args.auto else 10_000_000)
    cores = os.cpu_count() or 1
    max_tasks = args.max_tasks or cores * 2
    if args.auto:
        doubled = {2**i for i in range(20) if 2**i <= max_tasks}
        task_counts = sorted(doubled | {cores, max_tasks})
    else:
        task_counts = sorted({1, 2, cores, max_tasks})
    print(f"cores = {cores}, total = {total}")

    results: list[tuple[int, float]] = []
    with ProcessPoolExecutor() as pool:
        list(pool.map(work_chunk, [1]))  # Warm up, not timed
        baseline: float | None = None
        for tasks in task_counts:
            elapsed = timed_split(pool, total, tasks)
            baseline = baseline or elapsed
            speedup = baseline / elapsed
            results.append((tasks, speedup))
            print(
                f"{tasks:>3} tasks: {elapsed:6.3f}s "
                f"({speedup:4.2f}x)"
            )

    if args.auto:
        plot_speedups(results)

if __name__ == "__main__":
    main()
