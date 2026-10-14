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
                    if lhs is left and rhs is right:
                        # Share the unchanged subtree
                        return e
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
                    if lhs is left and rhs is right:
                        return e
                    return Mul(lhs, rhs)
        case _:
            assert_never(e)
