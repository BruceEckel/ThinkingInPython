# test_iterators.py
from iterators import Countdown, fibonacci, total

def test_fibonacci_sequence() -> None:
    assert list(fibonacci(8)) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert list(fibonacci(0)) == []
    assert list(fibonacci(1)) == [0]

def test_countdown_sequence() -> None:
    assert list(Countdown(5)) == [5, 4, 3, 2, 1]
    assert list(Countdown(0)) == []

def test_countdown_is_reiterable() -> None:
    c = Countdown(3)
    assert list(c) == [3, 2, 1]
    assert list(c) == [3, 2, 1]  # __iter__ yields a fresh generator

def test_total_over_any_iterable() -> None:
    assert total([1, 2, 3, 4]) == 10
    assert total(fibonacci(8)) == 33
    assert total(Countdown(5)) == 15
