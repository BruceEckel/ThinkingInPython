# rust/fastcount/demo.py
import timeit
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
    lengths = []
    for start in values:
        n = start
        steps = 0
        while n != 1:
            n = n // 2 if n % 2 == 0 else 3 * n + 1
            steps += 1
        lengths.append(steps)
    return lengths

limit = 200_000
assert fastcount.count_primes(limit) == count_primes(limit)
t_python = timeit.timeit(lambda: count_primes(limit), number=1)
t_rust = timeit.timeit(lambda: fastcount.count_primes(limit), number=1)
print(f"count_primes Rust speedup: {t_python / t_rust:.1f}x")
# Sample run: count_primes Rust speedup: 12.2x

values = list(range(1, 50_000))
assert fastcount.collatz_lengths(values) == collatz_lengths(values)
t_python = timeit.timeit(lambda: collatz_lengths(values), number=1)
t_rust = timeit.timeit(lambda: fastcount.collatz_lengths(values), number=1)
print(f"collatz_lengths Rust speedup: {t_python / t_rust:.1f}x")
# Sample run: collatz_lengths Rust speedup: 34.3x
