# thread_vs_task_speed.py
import asyncio
import threading
import time

COUNT = 3000

def noop() -> None:
    pass

async def async_noop() -> None:
    pass

def spawn_threads() -> float:
    start = time.perf_counter()
    threads = [threading.Thread(target=noop) for _ in range(COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start

async def spawn_async_tasks() -> float:
    start = time.perf_counter()
    await asyncio.gather(*(async_noop() for _ in range(COUNT)))
    return time.perf_counter() - start

t_threads = spawn_threads()
t_tasks = asyncio.run(spawn_async_tasks())
print(f"tasks at least 5x faster to spawn: {t_tasks * 5 < t_threads}")
#: tasks at least 5x faster to spawn: True
