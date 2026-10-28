# test_chain.py
from algorithms import (Fn, Hint, Root, RootFinder,
                        bisection, newton, secant)
from chain import first_root

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

def watched(finder: RootFinder,
            tried: list[str]) -> RootFinder:
    def recording(f: Fn, a: Hint,
                  b: Hint) -> Root | None:
        tried.append(finder.__name__)  # type: ignore
        return finder(f, a, b)
    return recording

def test_first_successful_finder_wins() -> None:
    tried: list[str] = []
    chain = [watched(x, tried)
             for x in (bisection, secant, newton)]
    root = first_root(f, 0.0, 2.0, chain)
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6
    assert tried == ["bisection"]  # The rest never ran

def test_chain_falls_through_to_a_later_method() -> None:
    assert f(1.0) * f(1.3) > 0  # No bracket
    assert bisection(f, 1.0, 1.3) is None
    tried: list[str] = []
    chain = [watched(x, tried)
             for x in (bisection, secant, newton)]
    root = first_root(f, 1.0, 1.3, chain)
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6
    assert tried == ["bisection", "secant"]

def test_empty_chain_returns_none() -> None:
    assert first_root(f, 0.0, 2.0, []) is None

def test_all_fail_returns_none() -> None:
    def g(x: float) -> float:
        return x * x + 1  # No real root
    chain: list[RootFinder] = [bisection, secant, newton]
    assert first_root(g, 0.0, 2.0, chain) is None
