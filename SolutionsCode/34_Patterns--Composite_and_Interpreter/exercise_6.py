# exercise_6.py
from dataclasses import dataclass

class Operators:
    def __add__(self: Expr, other: Expr | int) -> Add:
        if isinstance(other, Operators | int):
            return Add(self, wrap(other))
        return NotImplemented

    def __radd__(self: Expr, other: int) -> Add:
        if isinstance(other, int):
            return Add(Num(other), self)
        return NotImplemented

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        if isinstance(other, Operators | int):
            return Mul(self, wrap(other))
        return NotImplemented

    def __rmul__(self: Expr, other: int) -> Mul:
        if isinstance(other, int):
            return Mul(Num(other), self)
        return NotImplemented

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

x = Var("x")
print(type(2 * x + 1).__name__, (2 * x + 1).right)
#: Add Num(value=1)
try:
    "a" + x  # type: ignore
except TypeError as e:
    print(type(e).__name__, e)
#: TypeError can only concatenate str (not "Var") to str
try:
    x + "a"  # type: ignore
except TypeError as e:
    print(e)  # Same exception type, other message
#: unsupported operand type(s) for +: 'Var' and 'str'
