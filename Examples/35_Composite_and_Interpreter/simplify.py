# simplify.py
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

def simplify(e: Expr) -> Expr:
    match e:
        case Num(_) | Var(_):
            return e
        case Add(left, right):
            lhs, rhs = simplify(left), simplify(right)
            match (lhs, rhs):
                case (Num(0), other) | (other, Num(0)):
                    return other
                case (Num(a), Num(b)):
                    return Num(a + b)
                case _:
                    return Add(lhs, rhs)
        case Mul(left, right):
            lhs, rhs = simplify(left), simplify(right)
            match (lhs, rhs):
                case (Num(0), _) | (_, Num(0)):
                    return Num(0)
                case (Num(1), other) | (other, Num(1)):
                    return other
                case (Num(a), Num(b)):
                    return Num(a * b)
                case _:
                    return Mul(lhs, rhs)
        case _:
            assert_never(e)

if __name__ == "__main__":
    from infix import to_infix
    x = Var("x")
    messy = 1 * x + 0 * Var("y") + (Num(2) + 3) * x
    print(to_infix(messy))
    print(to_infix(simplify(messy)))
#: (((1 * x) + (0 * y)) + ((2 + 3) * x))
#: (x + (5 * x))
