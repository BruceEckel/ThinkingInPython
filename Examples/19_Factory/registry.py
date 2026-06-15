# registry.py
# A class is a first-class object, so a factory is just a dict of
# classes. __init_subclass__ lets each subclass register itself, so
# the factory never needs editing when you add a type.


class Shape:
    registry: dict[str, type["Shape"]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Shape.registry[cls.__name__] = cls

    def draw(self) -> None: ...


class Circle(Shape):
    def draw(self) -> None: print("Circle.draw")


class Square(Shape):
    def draw(self) -> None: print("Square.draw")


def make(name: str) -> Shape:
    return Shape.registry[name]()


for name in ["Circle", "Square", "Circle"]:
    make(name).draw()
