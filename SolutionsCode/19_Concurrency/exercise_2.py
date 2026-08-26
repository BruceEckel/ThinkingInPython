# exercise_2.py
import asyncio
import time

async def fetch(item, delay):
    print(f"{item}: started")
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main():
    coroutines = [fetch("a", 0.03), fetch("b", 0.02),
                  fetch("c", 0.01)]
    start = time.perf_counter()
    results = [await c for c in coroutines]
    elapsed = time.perf_counter() - start
    print(results)
    print(
        f"took the sum, not the longest: {elapsed > 0.055}")

asyncio.run(main())
#: a: started
#: a: resumed
#: b: started
#: b: resumed
#: c: started
#: c: resumed
#: ['A', 'B', 'C']
#: took the sum, not the longest: True
