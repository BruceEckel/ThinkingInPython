# test_counting_proxy.py
from counting_proxy import CountingProxy

class Doubler:
    factor = 2
    def double(self, n: int) -> int:
        return n * self.factor

def test_proxy_forwards_call_and_result() -> None:
    p = CountingProxy(Doubler())
    assert p.double(5) == 10
    assert p.double(3) == 6

def test_proxy_counts_only_calls() -> None:
    p = CountingProxy(Doubler())
    assert p.factor == 2
    assert p.calls == 0
    p.double(1)
    p.double(1)
    assert p.calls == 2
