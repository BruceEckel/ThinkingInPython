# heterogeneous.py

person = ("Alice", 30, 1.65)  # Name, age, height
name, age, height = person
print(name, age, height)
#: Alice 30 1.65
print(person[0], type(person[0]).__name__)
#: Alice str
print(person[1], type(person[1]).__name__)
#: 30 int
print(person[2], type(person[2]).__name__)
#: 1.65 float
