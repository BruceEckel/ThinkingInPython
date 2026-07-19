# event_loop_boundary.py
import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

@dataclass
class Meter:
    active: int = 0
    peak: int = 0

    def __enter__(self) -> None:
        self.active += 1
        self.peak = max(self.peak, self.active)

    def __exit__(self, exc_type: object, exc: object,
                 tb: object) -> None:
        self.active -= 1

async def io_price(order: int, meter: Meter) -> int:
    with meter:
        await asyncio.sleep(0.05)  # Off-processor work
    return order * 10

async def cpu_price(order: int, meter: Meter) -> int:
    with meter:
        total = 0
        for _ in range(1_000_000):  # On-processor work
            total += 1
    return order * 10

# Defines an async function:
type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def run(price_task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
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
