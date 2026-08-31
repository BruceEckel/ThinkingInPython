# test_count_calls.py
from count_calls import count_calls

def test_counts_are_independent_per_function() -> None:
    @count_calls
    def greet() -> None:
        pass

    @count_calls
    def farewell() -> None:
        pass

    greet()
    greet()
    farewell()

    assert greet.count == 2
    assert farewell.count == 1
