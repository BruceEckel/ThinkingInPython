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

def run_on(
    executor: Executor, orders: list[int]
) -> list[int]:
    with executor:
        return list(executor.map(cpu_price, orders))

if __name__ == "__main__":
    orders = [1, 2, 3, 4, 5]
    backends: list[Executor] = [
        ThreadPoolExecutor(),
        ProcessPoolExecutor(),
        InterpreterPoolExecutor(),
    ]
    for b in backends:
        print(f"{type(b).__name__}: {run_on(b, orders)}")
