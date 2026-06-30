# functional_errors.py
def safe_divide(a: int, b: int) -> float | None:
    if b == 0:
        return None
    return a / b

for divisor in (2, 0):
    match safe_divide(10, divisor):
        case None:
            print("undefined")
        case value:
            print(value)
#: 5.0
#: undefined
