# test_fronting.py
from counting_proxy import CountingProxy
from state_demo import StateD


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
    assert p.answer == 42  # non-callable attribute passes through
    p2 = CountingProxy(Doubler())
    p2.double(1)
    p2.double(1)
    assert p.calls == 0
    assert p2.calls == 2


class StateA:
    def name(self) -> str:
        return "A"


class StateB:
    def name(self) -> str:
        return "B"


def test_state_delegates_and_change_imp_swaps() -> None:
    s = StateD(StateA())
    assert s.name() == "A"
    s.change_imp(StateB())
    assert s.name() == "B"
