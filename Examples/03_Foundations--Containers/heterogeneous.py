# heterogeneous.py

person = ("Alice", 30, 1.65)  # Name, age, height
name, age, height = person
print(name, age, height)
#: Alice 30 1.65
print(type(name).__name__, type(age).__name__,
      type(height).__name__)
#: str int float
