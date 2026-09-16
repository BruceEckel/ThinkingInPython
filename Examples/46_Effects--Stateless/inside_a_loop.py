# inside_a_loop.py
import asyncio
from exceptions import expect
from greeter import Console, greet
from stateless import run, run_async, supply

bound = supply(Console())(greet)

async def main() -> None:
    expect(RuntimeError, run, bound("Alice"))
    await run_async(bound("Bob"))

asyncio.run(main())
#: [RuntimeError] asyncio.run() cannot be called from a
#: running event loop
#: Hello, Bob!
