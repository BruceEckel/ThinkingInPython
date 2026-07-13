# test_simplify.py
from typing import Final
import pytest
from expr import Add, Expr, Mul, Num, Var
from simplify import simplify

X: Final[Var] = Var("x")

@pytest.mark.parametrize("expr, expected", [
    (X + 0, X),
    (0 + X, X),
    (1 * X, X),
    (X * 1, X),
])
def test_identity_elements_vanish(
    expr: Expr, expected: Expr,
) -> None:
    assert simplify(expr) == expected

def test_zero_absorbs_multiplication() -> None:
    assert simplify(Var("x") * 0) == Num(0)
    assert simplify(0 * Var("x")) == Num(0)

def test_constant_folding() -> None:
    assert simplify(Num(2) + 3) == Num(5)
    assert simplify(Num(2) * 3 + 4) == Num(10)

def test_rewriting_reaches_every_level() -> None:
    x = Var("x")
    assert simplify((x + 0) * (1 * x)) == Mul(x, x)

def test_already_simple_is_unchanged() -> None:
    x = Var("x")
    assert simplify(2 * x + 1) == Add(Mul(Num(2), x), Num(1))
