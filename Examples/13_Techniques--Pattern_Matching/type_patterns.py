# type_patterns.py

def describe(value: object) -> str:
    match value:
        case bool(b):
            return f"bool {b}"
        case int(n):
            return f"int {n}"
        case str(s):
            return f"str of length {len(s)}"
        case _:
            return "something else"

print(describe(True))
#: bool True
print(describe(7))
#: int 7
print(describe("hello"))
#: str of length 5
print(describe(3.5))
#: something else
