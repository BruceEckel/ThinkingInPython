# registry_demo.py
from exceptions import expect
from registry import Shape, make

print(sorted(Shape.registry))
#: ['Circle', 'Square']
for kind in ["Circle", "Square", "Circle"]:
    make(kind).draw()
#: Circle.draw
#: Square.draw
#: Circle.draw
expect(KeyError, make, "Triangle")
#: [KeyError] 'Triangle'
