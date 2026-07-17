# test_chain.py
from algorithms import bisection, newton, secant
from chain import solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

def test_first_successful_finder_wins() -> None:
    root = solve(f, 0.0, 2.0, [bisection, secant, newton])
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6

def test_chain_falls_through_to_a_later_method() -> None:
    # [1.0, 1.3] does not bracket the root: bisection fails
    root = solve(f, 1.0, 1.3, [bisection, secant, newton])
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6

def test_empty_chain_returns_none() -> None:
    assert solve(f, 0.0, 2.0, []) is None

def test_all_fail_returns_none() -> None:
    def g(x: float) -> float:
        return x * x + 1  # No real root
    assert solve(g, 0.0, 2.0, [bisection]) is None
