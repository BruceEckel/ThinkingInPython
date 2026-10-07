# object_narrowing.py

def describe(value: object) -> str:
    # ty: "object" has no attribute "upper":
    # return value.upper()
    if isinstance(value, str):
        return value.upper()
    return repr(value)  # [1]

print(describe("hi"))
#: HI
print(describe(42))
#: 42
