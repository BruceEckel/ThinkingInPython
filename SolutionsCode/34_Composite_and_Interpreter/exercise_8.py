# exercise_8.py
from dataclasses import dataclass
from enum import Enum
from typing import assert_never

class Operators:
    def __add__(self: Expr, other: Expr | int) -> Add:
        return Add(self, wrap(other))

    def __radd__(self: Expr, other: int) -> Add:
        return Add(Num(other), self)

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        return Mul(self, wrap(other))

    def __rmul__(self: Expr, other: int) -> Mul:
        return Mul(Num(other), self)

@dataclass(frozen=True)
class Num(Operators):
    value: int

@dataclass(frozen=True)
class Var(Operators):
    name: str

@dataclass(frozen=True)
class Add(Operators):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

def evaluate(e: Expr, /, **env: int) -> int:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return (evaluate(left, **env)
                    + evaluate(right, **env))
        case Mul(left, right):
            return (evaluate(left, **env)
                    * evaluate(right, **env))
        case _:
            assert_never(e)

# A pending combine, behind the children it consumes:
class Op(Enum):
    ADD = "+"
    MUL = "*"

def evaluate_iterative(e: Expr, /, **env: int) -> int:
    work: list[Expr | Op] = [e]
    values: list[int] = []
    while work:
        item = work.pop()
        match item:
            case Op.ADD:
                right_value, left_value = (
                    values.pop(), values.pop())
                values.append(left_value + right_value)
            case Op.MUL:
                right_value, left_value = (
                    values.pop(), values.pop())
                values.append(left_value * right_value)
            case Num(value):
                values.append(value)
            case Var(name):
                values.append(env[name])
            case Add(left, right):
                work += [Op.ADD, right, left]
            case Mul(left, right):
                work += [Op.MUL, right, left]
            case _:
                assert_never(item)
    return values.pop()

deep: Expr = Num(0)
for n in range(1, 2001):
    deep = deep + Num(n)

try:
    evaluate(deep)
except RecursionError as e:
    print(type(e).__name__)
#: RecursionError
print(evaluate_iterative(deep))
#: 2001000

x = Var("x")
small = 2 * x + 1
print(evaluate(small, x=3), evaluate_iterative(small, x=3))
#: 7 7
