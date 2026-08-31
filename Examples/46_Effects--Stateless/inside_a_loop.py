# inside_a_loop.py
import asyncio
from greeter import Console, greet
from stateless import run, run_async, supply

bound = supply(Console())(greet)

async def main() -> None:
    try:
        run(bound("Alice"))
    except RuntimeError as e:
        print(e)
    await run_async(bound("Bob"))

asyncio.run(main())
#: asyncio.run() cannot be called from a running event loop
#: Hello, Bob!
