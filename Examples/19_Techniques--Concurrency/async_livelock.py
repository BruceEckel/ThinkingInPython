# async_livelock.py
import asyncio

wants: dict[str, bool] = {"a": True, "b": True}

async def giver(me: str, other: str) -> None:
    for _ in range(3):
        if wants[other]:
            print(f"{me}: gives")
        else:
            print(f"{me}: proceeds")
            wants[me] = False
        await asyncio.sleep(0)

async def main() -> None:
    await asyncio.gather(giver("a", other="b"),
                         giver("b", other="a"))
    print(f"resolved: {not any(wants.values())}")

asyncio.run(main())
#: a: gives
#: b: gives
#: a: gives
#: b: gives
#: a: gives
#: b: gives
#: resolved: False
