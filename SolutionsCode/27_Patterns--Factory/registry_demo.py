# registry_demo.py
import extra_shapes  # noqa: F401
from exceptions import expect
from registry import Shape, make

print(sorted(Shape.registry))
#: ['Circle', 'Square']
for name in ["Circle", "Square", "Circle"]:
    make(name).draw()
#: Circle.draw
#: Square.draw
#: Circle.draw
expect(KeyError, make, "Triangle")
#: [KeyError] 'Triangle'
