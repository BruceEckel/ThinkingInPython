# parallel_cpu.py
from concurrent.futures import ProcessPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

def main() -> None:
    orders = [1, 2, 3, 4, 5]
    with ProcessPoolExecutor() as pool:
        prices = list(pool.map(cpu_price, orders))
    print(prices)

if __name__ == "__main__":
    main()
