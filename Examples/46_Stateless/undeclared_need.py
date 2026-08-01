# undeclared_need.py
from greet_all import greet
from stateless import Success

def greet_all(names: list[str]) -> Success[None]:
    for name in names:
        yield from greet(name)  # type: ignore
