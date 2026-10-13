# parallel_cpu.py
from concurrent.futures import ProcessPoolExecutor
from pricing import cpu_price

if __name__ == "__main__":
    orders = [1, 2, 3, 4, 5]
    with ProcessPoolExecutor() as pool:
        prices = list(pool.map(cpu_price, orders))
    print(prices)
