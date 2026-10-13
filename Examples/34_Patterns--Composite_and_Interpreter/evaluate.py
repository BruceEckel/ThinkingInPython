# evaluate.py
from collections.abc import Mapping
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

def evaluate(e: Expr, env: Mapping[str, int]) -> int:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return (evaluate(left, env)
                    + evaluate(right, env))
        case Mul(left, right):
            return (evaluate(left, env)
                    * evaluate(right, env))
        case _:
            assert_never(e)

if __name__ == "__main__":
    x = Var("x")
    expr = 2 * x + 1
    print(evaluate(expr, {"x": 3}),
          evaluate(expr, {"x": 10}))
#: 7 21
