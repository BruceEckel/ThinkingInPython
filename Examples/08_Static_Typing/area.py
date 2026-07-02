# area.py
def area(width: int, height: int) -> int:
    return width * height

# ty: argument of type "str" is not assignable to "int":
print(area("3", 4))  # type: ignore
#: 3333
