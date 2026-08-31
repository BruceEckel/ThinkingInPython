# async_livelock.py
import asyncio

a_wants = True
b_wants = True

async def giver(name: str) -> None:
    global a_wants, b_wants
    for _ in range(3):
        other_wants = b_wants if name == "a" else a_wants
        if other_wants:
            print(f"{name}: gives")
        else:
            print(f"{name}: proceeds")
            if name == "a":
                a_wants = False
            else:
                b_wants = False
        await asyncio.sleep(0)

async def main() -> None:
    await asyncio.gather(giver("a"), giver("b"))
    print(f"resolved: {not (a_wants or b_wants)}")

asyncio.run(main())
#: a: gives
#: b: gives
#: a: gives
#: b: gives
#: a: gives
#: b: gives
#: resolved: False
