# exercise_5.py
from __future__ import annotations
from dataclasses import dataclass
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

def to_infix(e: Expr) -> str:
    match e:
        case Num(value):
            return str(value)
        case Var(name):
            return name
        case Add(left, right):
            return f"{to_infix(left)} + {to_infix(right)}"
        case Mul(left, right):
            return f"{to_infix(left)} * {to_infix(right)}"

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

def derivative(e: Expr, name: str) -> Expr:
    match e:
        case Num(_):
            return Num(0)
        case Var(n):
            return Num(1) if n == name else Num(0)
        case Add(left, right):  # Sum rule: (f + g)' = f' + g'
            return Add(derivative(left, name),
                       derivative(right, name))
        case Mul(left, right):  # Product rule: (fg)' = f'g + fg'
            return Add(Mul(derivative(left, name), right),
                       Mul(left, derivative(right, name)))
        case _:
            assert_never(e)

x = Var("x")
d = derivative(x * x, "x")
print(to_infix(d))
#: 1 * x + x * 1
print(to_infix(simplify(d)))
#: x + x
