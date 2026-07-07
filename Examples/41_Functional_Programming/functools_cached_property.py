# functools_cached_property.py
from functools import cached_property

class Lazy:
    def __init__(self, n: int) -> None:
        self.n = n

    @cached_property
    def squared(self) -> int:
        print("computing")
        return self.n * self.n

x = Lazy(5)
print(x.squared)
#: computing
#: 25
print(x.squared)  # No second "computing"
#: 25
