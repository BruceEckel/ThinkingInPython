# exercise_3.py
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

    def __neg__(self: Expr) -> Neg:
        return Neg(self)

    def __truediv__(self: Expr, other: Expr | int) -> Div:
        return Div(self, wrap(other))

    def __rtruediv__(self: Expr, other: int) -> Div:
        return Div(Num(other), self)

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

@dataclass(frozen=True)
class Neg(Operators):
    operand: Expr

@dataclass(frozen=True)
class Div(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul | Neg | Div

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

def evaluate(e: Expr, **env: int) -> float:
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
        case Neg(operand):
            return -evaluate(operand, **env)
        case Div(left, right):
            return (evaluate(left, **env)
                    / evaluate(right, **env))
        case _:
            assert_never(e)

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
        case Neg(operand):
            return f"-{to_infix(operand)}"
        case Div(left, right):
            return f"({to_infix(left)} / {to_infix(right)})"
        case _:
            assert_never(e)

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
        case Neg(operand):
            match simplify(operand):
                case Num(a):
                    return Num(-a)
                case Neg(deeper):
                    return deeper  # Double negation
                case inner:
                    return Neg(inner)
        case Div(left, right):
            # Division by Num(0) is deliberately left alone:
            return Div(simplify(left), simplify(right))
        case _:
            assert_never(e)

x = Var("x")
expr = (2 * x + 1) / -x
print(to_infix(expr))
#: (((2 * x) + 1) / -x)
print(evaluate(expr, x=3))
#: -2.3333333333333335
print(to_infix(simplify(Neg(Neg(x)) + Num(0))))
#: x
