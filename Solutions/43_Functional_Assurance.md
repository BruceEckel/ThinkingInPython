# Functional Assurance: Solutions

## 1. A fifth limit added to the parallel prime count

```python
from concurrent.futures import ProcessPoolExecutor

def count_primes(limit):
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count

def main():
    limits = [10_000, 20_000, 30_000, 40_000, 50_000]
    serial = list(map(count_primes, limits))
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(count_primes, limits))
    assert parallel == serial
    print(parallel)

if __name__ == "__main__":
    main()
```

`ProcessPoolExecutor` needs `count_primes` picklable and importable
from `__main__` in a worker process, which only holds for a real
script file, not a fenced block executed in place; run as a script,
this prints `[1229, 2262, 3245, 4203, 5133]`. The `assert` still passes
with a fifth limit added, for the same reason it passed with four:
`count_primes()` is pure, so calling it with `50_000` returns the
identical result whether the call runs in the main process (as part
of `serial`) or in a worker process (as part
of `parallel`). Growing the input list needed no change to
`count_primes()` itself, no new locks, and no new coordination code,
because purity was the only thing making the original four calls safe
to parallelize, and that property does not weaken as more calls are
added.
