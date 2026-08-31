# exercise_1a.py
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Leaky:
    def __init__(self, numbers, tags):
        self._numbers = numbers
        self._bob = Bob()
        self._tags = tags

    @property
    def tags(self):
        return self._tags

leaky = Leaky([1, 2], ["a", "b"])
leaky.tags.append("z")
print(leaky.tags)
#: ['a', 'b', 'z']
