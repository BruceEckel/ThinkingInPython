# exercise_7.py
from collections import namedtuple

Person = namedtuple("Person", ["name", "age", "height"])
person = Person("Alice", 30, 1.65)
# Unchanged from the tuple version
name, age, height = person
print(name, age, height)
#: Alice 30 1.65
# Now also reachable by name
print(person.name, person.height)
#: Alice 1.65
print(person[0], type(person[0]).__name__)
#: Alice str
