# coroutines_are_descriptions.py
import asyncio

ran: list[str] = []

async def greet() -> str:
    ran.append("body")
    return "Hello"

description = greet()  # Nothing runs
print(type(description).__name__, ran)
#: coroutine []
print(asyncio.run(description), ran)
#: Hello ['body']
