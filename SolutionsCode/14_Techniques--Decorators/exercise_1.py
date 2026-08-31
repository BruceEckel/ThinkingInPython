# exercise_1.py
def announce[T: type](cls: T) -> T:
    print(f"decorating {cls.__name__}")
    return cls

@announce
class Point:
    x: int
    y: int

@announce
class Empty:
    pass

print(Point.__name__, Empty.__name__)
#: decorating Point
#: decorating Empty
#: Point Empty
