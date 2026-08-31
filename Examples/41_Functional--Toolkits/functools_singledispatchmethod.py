# functools_singledispatchmethod.py
from functools import singledispatchmethod

class Describer:
    @singledispatchmethod
    def describe(self, value: object) -> str:
        return f"a {type(value).__name__}"

    @describe.register
    def _(self, value: int) -> str:
        return f"the number {value}"

d = Describer()
print(d.describe("hi"), "|", d.describe(5))
#: a str | the number 5
