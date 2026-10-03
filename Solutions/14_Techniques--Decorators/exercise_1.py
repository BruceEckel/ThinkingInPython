# exercise_1.py
def announce[T](cls: type[T]) -> type[T]:
    print(f"decorating {cls.__name__}")
    return cls

@announce
class Point:
    x: int
    y: int
#: decorating Point

@announce
class Empty:
    pass
#: decorating Empty

print(Point.__name__, Empty.__name__)
#: Point Empty
