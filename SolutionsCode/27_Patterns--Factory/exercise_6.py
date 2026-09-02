# exercise_6.py
import registry

print(registry.Shape.registry)
#: {}
try:
    registry.make("Circle")
except KeyError as e:
    print("KeyError:", e)
#: KeyError: 'Circle'

import extra_shapes  # noqa: E402  (the import is the point)

print(sorted(registry.Shape.registry))
#: ['Circle', 'Square']
registry.make("Circle").draw()
#: Circle.draw
print(extra_shapes.Circle.__name__)
#: Circle
