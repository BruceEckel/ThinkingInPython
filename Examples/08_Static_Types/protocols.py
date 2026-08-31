# protocols.py
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def draw(self) -> str:
        return "circle"

class Square:
    def draw(self) -> str:
        return "square"

def render(shape: Drawable) -> str:
    return shape.draw()

class Blob:
    def paint(self) -> str:
        return "blob"

print(render(Circle()))
#: circle
print(render(Square()))
#: square
# ty: expected "Drawable", found "Blob":
# render(Blob())
