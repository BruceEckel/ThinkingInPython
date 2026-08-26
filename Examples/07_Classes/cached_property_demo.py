# cached_property_demo.py
from functools import cached_property

class Numbers:
    def __init__(self, values):
        self.values = values

    @cached_property
    def total(self):
        print("summing", len(self.values), "values")
        return sum(self.values)

n = Numbers([5, 10, 15])
print(n.total)
#: summing 3 values
#: 30
# Second access: stored value, no recomputation
print(n.total)
#: 30
n.values.append(20)
print(n.total)  # Still the old sum: the cache is stale
#: 30
del n.total  # Discard the cached value
print(n.total)
#: summing 4 values
#: 50
