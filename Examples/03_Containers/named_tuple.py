# named_tuple.py
from collections import namedtuple

Person = namedtuple("Person", ["name", "age", "height"])
alice = Person("Alice", 30, 1.65)
print(alice)
#: Person(name='Alice', age=30, height=1.65)
print(alice.name, alice.age)  # Access by name
#: Alice 30
print(alice[0])  # Still indexable like a tuple
#: Alice
name, age, height = alice  # And unpackable
print(height)
#: 1.65
