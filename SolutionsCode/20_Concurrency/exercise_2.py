# exercise_2.py
import asyncio

class Meter:
    def __init__(self):
        self.active = 0
        self.peak = 0

    def enter(self):
        self.active += 1
        self.peak = max(self.peak, self.active)

    def leave(self):
        self.active -= 1

async def run(task, orders):
    meter = Meter()
    coros = [task(o, meter) for o in orders]
    prices = await asyncio.gather(*coros)
    return prices, meter.peak

async def mixed_price(order, meter):
    meter.enter()
    await asyncio.sleep(0.05)   # Waiting outside the processor
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    meter.leave()
    return order * 10

async def main():
    orders = [1, 2, 3, 4, 5]
    prices, peak = await run(mixed_price, orders)
    print(f"mixed peak={peak}, prices={prices}")

asyncio.run(main())
#: mixed peak=5, prices=[10, 20, 30, 40, 50]
