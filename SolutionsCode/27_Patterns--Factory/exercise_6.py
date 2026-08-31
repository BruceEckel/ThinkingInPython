# exercise_6.py
import shape_registry

print(shape_registry.Shape.registry)
#: {}
try:
    shape_registry.make("Circle")
except KeyError as e:
    print("KeyError:", e)
#: KeyError: 'Circle'

import extra_shapes  # noqa: E402  (the import is the point)

print(sorted(shape_registry.Shape.registry))
#: ['Circle', 'Square']
shape_registry.make("Circle").draw()
#: Circle.draw
print(extra_shapes.Circle.__name__)
#: Circle
