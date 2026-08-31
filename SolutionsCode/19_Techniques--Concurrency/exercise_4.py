# exercise_4.py
import asyncio
import time
from dataclasses import dataclass

@dataclass
class Meter:
    active: int = 0
    peak: int = 0

    def __enter__(self):
        self.active += 1
        self.peak = max(self.peak, self.active)

    def __exit__(self, exc_type, exc, tb):
        self.active -= 1

async def io_price(order, meter):
    with meter:
        time.sleep(0.05)  # Blocking, and never awaited
    return order * 10

async def run(price_task, orders):
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
    return prices, meter.peak

async def main():
    prices, peak = await run(io_price, [1, 2, 3, 4, 5])
    print(f"blocking peak={peak}, prices={prices}")

asyncio.run(main())
#: blocking peak=1, prices=[10, 20, 30, 40, 50]
