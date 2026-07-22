# thread_compare.py
import timeit
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

def compare(
    price: Callable[[int], int], orders: list[int], number: int
) -> tuple[float, float]:
    def sequential() -> list[int]:
        return [price(o) for o in orders]

    def threaded() -> list[int]:
        with ThreadPoolExecutor() as pool:
            return list(pool.map(price, orders))

    assert threaded() == sequential()
    t_seq = timeit.timeit(sequential, number=number)
    t_thr = timeit.timeit(threaded, number=number)
    return t_seq, t_thr
