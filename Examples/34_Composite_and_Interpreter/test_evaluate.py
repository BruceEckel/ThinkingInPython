# test_evaluate.py
import pytest
from evaluate import evaluate
from expr import Add, Mul, Num, Var

def test_literal_and_variable() -> None:
    assert evaluate(Num(42)) == 42
    assert evaluate(Var("x"), x=3) == 3

def test_operators_build_the_tree() -> None:
    x = Var("x")
    assert 2 * x + 1 == Add(Mul(Num(2), x), Num(1))
    assert 1 + x == Add(Num(1), x)
    assert x * x == Mul(x, x)

def test_one_tree_many_environments() -> None:
    area = Var("w") * Var("h")
    assert evaluate(area, w=2, h=3) == 6
    assert evaluate(area, w=10, h=10) == 100

def test_unbound_variable_raises() -> None:
    with pytest.raises(KeyError):
        evaluate(Var("y"), x=1)
