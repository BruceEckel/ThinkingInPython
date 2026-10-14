# run_cost.py
import asyncio
import time
from typing import Final
from benchmark import report
from exceptions import expected
from stateless import Success, run, run_async, success

def trivial(n: int) -> Success[int]:
    return success(n)

async def inside_loop() -> None:
    with expected(RuntimeError):
        run(trivial(1))

asyncio.run(inside_loop())
#: [RuntimeError] asyncio.run() cannot be called from a
#: running event loop

ROUNDS: Final[int] = 2000

def time_run() -> float:
    start = time.perf_counter()
    for _ in range(ROUNDS):
        run(trivial(1))
    return (time.perf_counter() - start) / ROUNDS

async def time_run_async() -> float:
    start = time.perf_counter()
    for _ in range(ROUNDS):
        await run_async(trivial(1))
    return (time.perf_counter() - start) / ROUNDS

per_run = time_run()
per_run_async = asyncio.run(time_run_async())
report(per_run=per_run, per_run_async=per_run_async)
print(f"run() at least 20x slower: "
      f"{per_run > per_run_async * 20}")
#: run() at least 20x slower: True
