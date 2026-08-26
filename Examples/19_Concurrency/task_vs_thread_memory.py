# task_vs_thread_memory.py
import asyncio
import threading
import tracemalloc
from typing import Final
from benchmark import report

TASKS: Final[int] = 5_000
# 1 MiB, a common thread stack reservation:
STACK_SIZE: Final[int] = 1024 * 1024

async def parked() -> None:
    await asyncio.sleep(999)  # Suspended, never resumes

async def bytes_per_task() -> float:
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    tasks = [asyncio.create_task(parked())
             for _ in range(TASKS)]
    # Let every task reach its own await
    await asyncio.sleep(0)
    after = tracemalloc.take_snapshot()
    grown = sum(
        stat.size_diff
        for stat in after.compare_to(before, "lineno")
        if stat.size_diff > 0
    )
    for t in tasks:
        t.cancel()
    # Without "return_exceptions=True", the first
    # CancelledError raises and exits the function:
    await asyncio.gather(*tasks, return_exceptions=True)
    tracemalloc.stop()
    return grown / TASKS

default_stack = threading.stack_size()
threading.stack_size(STACK_SIZE)  # A real, settable cost
configured_stack = threading.stack_size()
# Restore the previous setting
threading.stack_size(default_stack)

task_cost = asyncio.run(bytes_per_task())
tasks_per_stack = configured_stack / task_cost
report(bytes_per_task=task_cost,
       tasks_per_stack=tasks_per_stack)
print(f"one thread's stack reservation: "
      f"{configured_stack:,} bytes")
#: one thread's stack reservation: 1,048,576 bytes
print(f"bytes per task under 4 KiB: {task_cost < 4096}")
#: bytes per task under 4 KiB: True
print(f"holds over 200 tasks: {tasks_per_stack > 200}")
#: holds over 200 tasks: True
