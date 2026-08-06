# exercise_1.py
def slots_report[T: type](cls: T) -> T:
    print(f"decorating {cls.__name__}")
    return cls

@slots_report
class Point:
    x: int
    y: int

@slots_report
class Empty:
    pass

print(Point.__name__, Empty.__name__)
#: decorating Point
#: decorating Empty
#: Point Empty
