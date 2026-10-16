# rust/fastcount/demo.py
import timeit
from collections.abc import Callable
import fastcount

def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        for d in range(2, int(n**0.5) + 1):
            if n % d == 0:
                break
        else:
            count += 1
    return count

def collatz_lengths(values: list[int]) -> list[int]:
    lengths: list[int] = []
    for start in values:
        n = start
        steps = 0
        while n != 1:
            n = n // 2 if n % 2 == 0 else 3 * n + 1
            steps += 1
        lengths.append(steps)
    return lengths

def speedup[T, R](
    name: str, slow: Callable[[T], R],
    fast: Callable[[T], R], arg: T,
) -> None:
    assert fast(arg) == slow(arg)
    t_slow = timeit.timeit(lambda: slow(arg), number=1)
    t_fast = timeit.timeit(lambda: fast(arg), number=1)
    print(f"{name} Rust speedup: {t_slow / t_fast:.1f}x")

speedup("count_primes", count_primes,
        fastcount.count_primes, 200_000)
# Sample run: count_primes Rust speedup: 12.3x
speedup("collatz_lengths", collatz_lengths,
        fastcount.collatz_lengths, list(range(1, 50_000)))
# Sample run: collatz_lengths Rust speedup: 36.0x
