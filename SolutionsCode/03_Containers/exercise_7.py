# exercise_7.py
from collections import namedtuple

Person = namedtuple("Person", ["name", "age", "height"])
person = Person("Alice", 30, 1.65)
name, age, height = person  # Unchanged from the tuple version
print(name, age, height)
#: Alice 30 1.65
print(person.name, person.height)  # Now also reachable by name
#: Alice 1.65
print(person[0], type(person[0]).__name__)
#: Alice str
