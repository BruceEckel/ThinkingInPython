# test_state.py
from state_demo import StateD

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
