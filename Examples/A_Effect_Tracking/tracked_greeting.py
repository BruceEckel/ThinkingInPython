# tracked_greeting.py
from typing import Annotated
from effect_rows import performs, row

class Ask: ...
class Tell: ...

def ask(prompt: str) -> Annotated[str, performs(Ask)]:
    return input(prompt)

def tell(message: str) -> Annotated[None, performs(Tell)]:
    print(message)

def greet() -> Annotated[None, performs(Ask, Tell)]:
    name: str = ask("What is your name? ")
    tell(f"Hello, {name}!")

def shout(message: str) -> None:
    tell(message.upper())

for f in ask, tell, greet, shout:
    print(f.__name__, row(f))
#: ask ['Ask']
#: tell ['Tell']
#: greet ['Ask', 'Tell']
#: shout []
