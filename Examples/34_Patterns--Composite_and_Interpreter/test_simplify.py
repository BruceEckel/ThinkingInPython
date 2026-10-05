# test_simplify.py
from typing import Final
import pytest
from expr import Expr, Mul, Num, Var
from simplify import simplify

X: Final[Var] = Var("x")

@pytest.mark.parametrize("expr, expected", [
    (X + 0, X),
    (0 + X, X),
    (1 * X, X),
    (X * 1, X),
])
def test_identity_returns_other_operand(
    expr: Expr, expected: Expr,
) -> None:
    assert simplify(expr) == expected

def test_multiplying_by_zero_gives_zero() -> None:
    assert simplify(X * 0) == Num(0)
    assert simplify(0 * X) == Num(0)

def test_constant_folding() -> None:
    assert simplify(Num(2) + 3) == Num(5)
    assert simplify(Num(2) * 3 + 4) == Num(10)

def test_rules_compose() -> None:
    assert simplify((X + 0) * (1 * X)) == Mul(X, X)

def test_already_simple_is_unchanged() -> None:
    expr = 2 * X + 1
    assert simplify(expr) is expr

def test_unchanged_subtrees_are_shared() -> None:
    keep = Var("w") * Var("h")
    assert simplify(keep + 0 * Var("z")) is keep
