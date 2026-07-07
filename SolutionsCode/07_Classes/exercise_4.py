# exercise_4.py
from functools import cached_property

class Numbers:
    def __init__(self, values):
        self.values = values

    @cached_property
    def total(self):
        print("summing", len(self.values), "values")
        return sum(self.values)

    @cached_property
    def average(self):
        print("computing average")
        return self.total / len(self.values)

n = Numbers([5, 10, 15])
print(n.total)
#: summing 3 values
#: 30
print(n.average)
#: computing average
#: 10.0
