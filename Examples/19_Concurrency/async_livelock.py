# async_livelock.py
import asyncio

a_wants = True
b_wants = True

async def yielder(name: str) -> None:
    global a_wants, b_wants
    for _ in range(3):
        other_wants = b_wants if name == "a" else a_wants
        if other_wants:
            print(f"{name}: yields")
        else:
            print(f"{name}: proceeds")
            if name == "a":
                a_wants = False
            else:
                b_wants = False
        await asyncio.sleep(0)

async def main() -> None:
    await asyncio.gather(yielder("a"), yielder("b"))
    print(f"resolved: {not (a_wants or b_wants)}")

asyncio.run(main())
#: a: yields
#: b: yields
#: a: yields
#: b: yields
#: a: yields
#: b: yields
#: resolved: False
