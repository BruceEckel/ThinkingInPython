# thread_compare.py
import timeit
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import NamedTuple

class Times(NamedTuple):
    sequential: float
    threaded: float

def compare(
    price: Callable[[int], int], orders: list[int], number: int
) -> Times:
    def sequential() -> list[int]:
        return [price(o) for o in orders]

    def threaded() -> list[int]:
        with ThreadPoolExecutor() as pool:
            return list(pool.map(price, orders))

    assert threaded() == sequential()
    return Times(
        min(timeit.repeat(sequential, number=number, repeat=3)),
        min(timeit.repeat(threaded, number=number, repeat=3)),
    )
