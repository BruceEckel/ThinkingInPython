# event_loop_boundary.py
import asyncio
from collections.abc import Awaitable, Callable

class Meter:
    def __init__(self) -> None:
        self.active = 0
        self.peak = 0

    def enter(self) -> None:
        self.active += 1
        self.peak = max(self.peak, self.active)

    def leave(self) -> None:
        self.active -= 1

type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def io_price(order: int, meter: Meter) -> int:
    meter.enter()
    await asyncio.sleep(0.05)   # Waiting outside the processor
    meter.leave()
    return order * 10

async def cpu_price(order: int, meter: Meter) -> int:
    meter.enter()
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    meter.leave()
    return order * 10

async def run(task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
    meter = Meter()
    coros = [task(o, meter) for o in orders]
    prices = await asyncio.gather(*coros)
    return prices, meter.peak

async def main() -> None:
    orders = [1, 2, 3, 4, 5]
    io_prices, io_peak = await run(io_price, orders)
    cpu_prices, cpu_peak = await run(cpu_price, orders)
    print(f"io : peak={io_peak}, prices={io_prices}")
    print(f"cpu: peak={cpu_peak}, prices={cpu_prices}")

asyncio.run(main())
#: io : peak=5, prices=[10, 20, 30, 40, 50]
#: cpu: peak=1, prices=[10, 20, 30, 40, 50]
