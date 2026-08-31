# infix.py
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

def to_infix(e: Expr) -> str:
    match e:
        case Num(value):
            return str(value)
        case Var(name):
            return name
        case Add(left, right):
            return f"({to_infix(left)} + {to_infix(right)})"
        case Mul(left, right):
            return f"({to_infix(left)} * {to_infix(right)})"
        case _:
            assert_never(e)

if __name__ == "__main__":
    x = Var("x")
    print(to_infix(2 * x + 1))
    print(to_infix((x + 1) * (x + 2)))
#: ((2 * x) + 1)
#: ((x + 1) * (x + 2))
