# parallel_pure.py
import time
from concurrent.futures import ProcessPoolExecutor
from benchmark import report

def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n**0.5) + 1)):
            count += 1
    return count

if __name__ == "__main__":
    limits = [200_000, 400_000, 600_000, 800_000]
    start = time.perf_counter()
    serial = list(map(count_primes, limits))
    serial_time = time.perf_counter() - start
    start = time.perf_counter()
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(count_primes, limits))
    parallel_time = time.perf_counter() - start
    assert parallel == serial
    report(serial=serial_time, parallel=parallel_time)
    print(parallel)
    #: [17984, 33860, 49098, 63951]
    faster = serial_time > 1.3 * parallel_time
    print(f"parallel at least 30% faster: {faster}")
    #: parallel at least 30% faster: True
