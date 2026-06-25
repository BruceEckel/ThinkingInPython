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

def render(shape: Drawable) -> str:   # Accepts anything with draw()
    return shape.draw()

print(render(Circle()))
## circle
print(render(Square()))
## square
