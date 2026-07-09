# coroutines_are_descriptions.py
import asyncio

async def greet() -> str:
    return "Hello"

description = greet()  # Nothing runs
print(type(description).__name__)
#: coroutine
print(asyncio.run(description))
#: Hello
