# any_executor.py
from concurrent.futures import (
    Executor,
    InterpreterPoolExecutor,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)
from pricing import Price, cpu_price

def run_on(
    executor: Executor, orders: list[int]
) -> list[Price]:
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
