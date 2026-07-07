# exercise_4.py
from __future__ import annotations
from dataclasses import dataclass

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

PRECEDENCE = {Add: 1, Mul: 2, Num: 3, Var: 3}

def to_infix(e: Expr, parent_prec: int = 0) -> str:
    match e:
        case Num(value):
            return str(value)
        case Var(name):
            return name
        case Add(left, right):
            prec = PRECEDENCE[Add]
            lhs = to_infix(left, prec)
            rhs = to_infix(right, prec + 1)
            s = f"{lhs} + {rhs}"
        case Mul(left, right):
            prec = PRECEDENCE[Mul]
            lhs = to_infix(left, prec)
            rhs = to_infix(right, prec + 1)
            s = f"{lhs} * {rhs}"
    my_prec = PRECEDENCE[type(e)]
    return f"({s})" if my_prec < parent_prec else s

x = Var("x")
print(to_infix(2 * x + 1))
#: 2 * x + 1
print(to_infix((x + 1) * (x + 2)))
#: (x + 1) * (x + 2)
