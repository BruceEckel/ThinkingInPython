# task_vs_thread_memory.py
import asyncio
import threading
import tracemalloc

TASKS = 20_000
STACK_SIZE = 1024 * 1024  # 1 MiB, a common thread stack reservation

async def parked() -> None:
    await asyncio.sleep(999)  # Suspended, never resumes

async def bytes_per_task() -> float:
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    tasks = [asyncio.ensure_future(parked()) for _ in range(TASKS)]
    await asyncio.sleep(0)  # Let every task reach its own await
    after = tracemalloc.take_snapshot()
    grown = sum(
        stat.size_diff
        for stat in after.compare_to(before, "lineno")
        if stat.size_diff > 0
    )
    for t in tasks:
        t.cancel()
    # Without "return_exceptions=True", the first CancelledError
    # would raise an exception and exit the function:
    await asyncio.gather(*tasks, return_exceptions=True)
    tracemalloc.stop()
    return grown / TASKS

default_stack = threading.stack_size()
threading.stack_size(STACK_SIZE)  # A real, settable cost
configured_stack = threading.stack_size()
threading.stack_size(default_stack)  # Restore the previous setting

task_cost = asyncio.run(bytes_per_task())
tasks_per_stack = configured_stack / task_cost
print(f"one thread's stack reservation: {configured_stack:,} bytes")
print(f"average bytes per task: {task_cost:.0f}")
print(f"tasks fitting in one thread's stack: {tasks_per_stack:.0f}")
print(f"holds over 200 tasks: {tasks_per_stack > 200}")
#: one thread's stack reservation: 1,048,576 bytes
#: average bytes per task: 1353
#: tasks fitting in one thread's stack: 775
#: holds over 200 tasks: True
