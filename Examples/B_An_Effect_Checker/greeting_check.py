# greeting_check.py
from row_check import check

GREETING = '''
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
report = check({"greeting": GREETING})
for name, row in report.rows.items():
    if row:
        print(name, sorted(row))
#: greeting.ask ['Ask']
#: greeting.tell ['Tell']
#: greeting.greet ['Ask', 'Tell']
#: greeting.shout ['Tell']
for finding in report.findings:
    print(finding.where, finding.problem)
#: greeting.ask undeclared Console
#: greeting.tell undeclared Console
#: greeting.quiet undeclared Tell
