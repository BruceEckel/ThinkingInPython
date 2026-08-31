# nested_patterns.py
from point import Point

def survey(points: list[Point]) -> str:
    match points:
        case [Point(0, 0) as start, *rest]:
            return f"{start} then {len(rest)} more"
        case [Point(0, n) | Point(n, 0)]:
            return f"one axis point, offset {n}"
        case [Point(), Point()]:
            return "two points"
        case _:
            return "nothing to say"

print(survey([Point(0, 0), Point(1, 1), Point(2, 2)]))
#: Point(x=0, y=0) then 2 more
print(survey([Point(0, 5)]))
#: one axis point, offset 5
print(survey([Point(4, 0)]))
#: one axis point, offset 4
print(survey([Point(1, 2), Point(3, 4)]))
#: two points
