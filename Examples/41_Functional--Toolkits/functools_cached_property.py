# functools_cached_property.py
from dataclasses import dataclass
from functools import cached_property

@dataclass
class Lazy:
    n: int

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
x.n = 10  # Doesn't change the cached result
print(x.squared)
#: 25
