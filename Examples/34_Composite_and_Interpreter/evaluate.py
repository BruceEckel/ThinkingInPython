# evaluate.py
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

def evaluate(e: Expr, **env: int) -> int:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return evaluate(left, **env) + evaluate(right, **env)
        case Mul(left, right):
            return evaluate(left, **env) * evaluate(right, **env)
        case _:
            assert_never(e)

if __name__ == "__main__":
    x = Var("x")
    expr = 2 * x + 1
    by_hand = Add(Mul(Num(2), x), Num(1))
    print(expr == by_hand)
    print(evaluate(expr, x=3), evaluate(expr, x=10))
#: True
#: 7 21
