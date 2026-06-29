# pattern_matching.py
def describe(value: object) -> str:
    match value:
        case 0:
            return "zero"
        case [x]:
            return f"one item: {x}"
        case [x, y]:
            return f"two items: {x}, {y}"
        case {"name": name}:
            return f"named {name}"
        case _:
            return "something else"

print(describe(0))
#: zero
print(describe([42]))
#: one item: 42
print(describe([1, 2]))
#: two items: 1, 2
print(describe({"name": "Ada"}))
#: named Ada
