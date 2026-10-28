# multiprocessing_raw.py
import multiprocessing as mp
from pricing import Price, cpu_price

type Priced = tuple[int, Price]  # (order, price)

def worker(order: int, results: mp.Queue[Priced]) -> None:
    results.put((order, cpu_price(order)))

if __name__ == "__main__":
    orders = [1, 2, 3, 4, 5]
    results: mp.Queue[Priced] = mp.Queue()
    workers = [
        mp.Process(target=worker, args=(order, results))
        for order in orders
    ]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    pairs = sorted(results.get() for _ in workers)
    print([price for _, price in pairs])
