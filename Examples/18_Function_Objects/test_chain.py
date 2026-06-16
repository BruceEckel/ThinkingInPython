# test_chain.py
from chain import Line, Result, bisection, least_squares, newtons_method, solve


def test_first_successful_handler_wins() -> None:
    assert solve(
        [1.0, 2.0, 3.0],
        [least_squares, newtons_method, bisection],
    ) == [5.5, 6.6]  # bisection


def test_order_decides_the_winner() -> None:
    def always(line: Line) -> Result:
        return [1.0]

    # 'always' precedes bisection, so it short-circuits the chain.
    assert solve([0.0], [always, bisection]) == [1.0]


def test_no_handler_succeeds_returns_none() -> None:
    assert solve([0.0], [least_squares, newtons_method]) is None


def test_empty_chain_returns_none() -> None:
    assert solve([0.0], []) is None
