# class_values.py

class Shape:
    pass

class Circle(Shape):
    pass

def make(kind: type[Shape]) -> Shape:
    return kind()  # Instantiate the class

shape = make(Circle)
print(type(shape).__name__)
#: Circle
