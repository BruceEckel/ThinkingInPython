# functools_singledispatch.py
from functools import singledispatch

@singledispatch
def describe(value: object) -> str:
    return f"a {type(value).__name__}"

@describe.register
def _(value: int) -> str:
    return f"the number {value}"

print(describe("hi"), "|", describe(5))
#: a str | the number 5
