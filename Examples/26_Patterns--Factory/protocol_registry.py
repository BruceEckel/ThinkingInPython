# protocol_registry.py
from shape_registry import ShapeFactory

make = ShapeFactory()

@make.register
class Circle:
    def draw(self) -> None: print("Circle.draw")

@make.register
class Square:
    def draw(self) -> None: print("Square.draw")

print(sorted(make.registry))
#: ['Circle', 'Square']
make("Circle").draw()
#: Circle.draw
# ty: Argument type `Blob` does not satisfy
# upper bound `Shape` of type variable `S`:
# @make.register
# class Blob:
#     pass
