# multiprocessing_raw.py
import multiprocessing as mp

def cpu_price(order: int, results: mp.Queue[tuple[int, int]]) -> None:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    results.put((order, order * 10))

if __name__ == "__main__":
    orders = [1, 2, 3, 4, 5]
    results: mp.Queue[tuple[int, int]] = mp.Queue()
    workers = [
        mp.Process(target=cpu_price, args=(order, results))
        for order in orders
    ]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    pairs = sorted(results.get() for _ in workers)
    print([price for _, price in pairs])
