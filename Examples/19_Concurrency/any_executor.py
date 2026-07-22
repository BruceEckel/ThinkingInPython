# any_executor.py
from concurrent.futures import (
    Executor,
    InterpreterPoolExecutor,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

def run_on(executor: Executor, orders: list[int]) -> list[int]:
    with executor:
        return list(executor.map(cpu_price, orders))

if __name__ == "__main__":
    orders = [1, 2, 3, 4, 5]
    backends: list[Executor] = [
        ThreadPoolExecutor(),
        ProcessPoolExecutor(),
        InterpreterPoolExecutor(),
    ]
    results = [run_on(b, orders) for b in backends]
    print(results[0])
    print(all(r == results[0] for r in results))
