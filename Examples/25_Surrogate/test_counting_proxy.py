# test_counting_proxy.py
from counting_proxy import CountingProxy

class Doubler:
    def double(self, n: int) -> int:
        return n * 2

def test_proxy_forwards_call_and_result() -> None:
    p = CountingProxy(Doubler())
    assert p.double(5) == 10
    assert p.double(3) == 6

def test_proxy_counts_only_calls() -> None:
    class HasValue:
        answer = 42

    p = CountingProxy(HasValue())
    assert p.answer == 42  # Non-callable attribute passes through
    p2 = CountingProxy(Doubler())
    p2.double(1)
    p2.double(1)
    assert p.calls == 0
    assert p2.calls == 2
