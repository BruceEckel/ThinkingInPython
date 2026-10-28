# exercise_4.py
import asyncio
import time
from collections.abc import Awaitable, Callable
from meter import Meter, Peak
from pricing import Price

async def io_price(order: int, meter: Meter) -> Price:
    with meter:
        time.sleep(0.05)  # Blocking, and never awaited
    return order * 10

type PriceTask = Callable[[int, Meter], Awaitable[Price]]

async def run(
    price_task: PriceTask, orders: list[int]
) -> tuple[list[Price], Peak]:
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
    return prices, meter.peak

async def main() -> None:
    prices, peak = await run(io_price, [1, 2, 3, 4, 5])
    print(f"blocking peak={peak}, prices={prices}")

asyncio.run(main())
#: blocking peak=1, prices=[10, 20, 30, 40, 50]
