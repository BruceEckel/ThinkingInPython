# test_leaky.py
from leaky import Leaky

def test_getter_leaks_internal_state() -> None:
    leaky = Leaky([1, 2])
    leaky.numbers.append(999)  # Changes the internal list
    assert leaky.numbers == [1, 2, 999]
