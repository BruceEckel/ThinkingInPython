# facade.py
from dataclasses import dataclass

@dataclass
class A:
    x: object

# Other classes that aren't exposed by the
# facade go here ...

class Facade:
    @staticmethod
    def make_a(x: object) -> A:
        return A(x)

# The client programmer gets the objects
# by calling the static methods:
print(Facade.make_a(1))
#: A(x=1)
