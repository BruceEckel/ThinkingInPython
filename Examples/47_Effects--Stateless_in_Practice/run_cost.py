# run_cost.py
import asyncio
import time
from stateless import Success, run, run_async, success

def bound(n: int) -> Success[int]:
    return success(n)

async def inside_loop() -> str:
    try:
        run(bound(1))
    except RuntimeError as e:
        return str(e)
    return "no error"

print(asyncio.run(inside_loop()))
#: asyncio.run() cannot be called from a running event loop

ROUNDS = 2000

def time_run() -> float:
    start = time.perf_counter()
    for _ in range(ROUNDS):
        run(bound(1))
    return (time.perf_counter() - start) / ROUNDS

async def time_run_async() -> float:
    start = time.perf_counter()
    for _ in range(ROUNDS):
        await run_async(bound(1))
    return (time.perf_counter() - start) / ROUNDS

per_run = time_run()
per_run_async = asyncio.run(time_run_async())
print(f"run() at least 50x slower: "
      f"{per_run > per_run_async * 50}")
#: run() at least 50x slower: True
