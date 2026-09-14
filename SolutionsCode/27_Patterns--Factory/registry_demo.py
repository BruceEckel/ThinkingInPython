# registry_demo.py
import extra_shapes  # noqa: F401
from registry import Shape, make

print(sorted(Shape.registry))
#: ['Circle', 'Square']
for kind in ["Circle", "Square", "Circle"]:
    make(kind).draw()
#: Circle.draw
#: Square.draw
#: Circle.draw
try:
    make("Triangle")
except KeyError as e:
    print("KeyError:", e)
#: KeyError: 'Triangle'
