# greeting_check.py
from typing import Final
from row_check import check, lines

GREETING: Final[str] = '''
from typing import Annotated
from effect_rows import performs

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

def quiet() -> Annotated[None, performs()]:
    shout("hi")
'''
for line in lines(check({"greeting": GREETING})):
    print(line)
#: greeting.ask ['Ask']
#: greeting.tell ['Tell']
#: greeting.greet ['Ask', 'Tell']
#: greeting.shout ['Tell']
#: ! greeting.ask undeclared Console
#: ! greeting.tell undeclared Console
#: ! greeting.quiet undeclared Tell
