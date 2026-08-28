# thread_compare.py
import timeit
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import NamedTuple

class Times(NamedTuple):
    sequential: float
    threaded: float

def compare(
    price: Callable[[int], int], orders: list[int],
    number: int
) -> Times:
    def sequential() -> list[int]:
        return [price(o) for o in orders]

    def threaded() -> list[int]:
        with ThreadPoolExecutor() as pool:
            return list(pool.map(price, orders))

    assert threaded() == sequential()
    seq: list[float] = []
    thr: list[float] = []
    for _ in range(5):  # Alternate: a load spike hits both
        seq.append(timeit.timeit(sequential, number=number))
        thr.append(timeit.timeit(threaded, number=number))
    return Times(min(seq), min(thr))
