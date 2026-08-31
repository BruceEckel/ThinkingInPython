# exercise_5.py
import asyncio

PRICES = {"apple": 1.5, "pear": 2.0}

def price_of(item: str) -> float:
    return PRICES[item]

def total_price(items: list[str]) -> float:
    return sum(price_of(item) for item in items)

async def price_of_async(item: str) -> float:
    await asyncio.sleep(0)
    return PRICES[item]

async def total_price_async(items: list[str]) -> float:
    return sum(
        [await price_of_async(item) for item in items])

basket = ["apple", "pear"]
print(total_price(basket))
#: 3.5
print(asyncio.run(total_price_async(basket)))
#: 3.5
description = price_of_async("apple")
print(type(description).__name__)
#: coroutine
description.close()  # Never awaited, so close it explicitly
