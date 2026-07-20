# gather_with_exceptions.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    if item == "c":
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()

async def main() -> None:
    pairs = [
        ("a", 0.01),
        ("b", 0.02),
        ("c", 0.03),
        ("d", 0.2),
        ("e", 0.3),
    ]
    results = await asyncio.gather(
        *(fetch(item, delay) for item, delay in pairs),
        return_exceptions=True,
    )
    for (item, _), result in zip(pairs, results):
        if isinstance(result, BaseException):
            print(f"{item}: raised {result!r}")
        else:
            print(f"{item}: {result}")

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: e: started
#: a: fetched
#: b: fetched
#: d: fetched
#: e: fetched
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: D
#: e: E
