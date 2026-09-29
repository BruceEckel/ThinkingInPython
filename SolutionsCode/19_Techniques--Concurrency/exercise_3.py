# exercise_3.py
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

async def mixed_price(order: int, meter: Meter) -> int:
    with meter:
        # Waiting, off the processor
        await asyncio.sleep(0.05)
        total = 0
        # Working, on the processor
        for _ in range(1_000_000):
            total += 1
    return order * 10

type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def run(price_task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
    return prices, meter.peak

async def main() -> None:
    prices, peak = await run(mixed_price, [1, 2, 3, 4, 5])
    print(f"mixed peak={peak}, prices={prices}")

asyncio.run(main())
#: mixed peak=5, prices=[10, 20, 30, 40, 50]
