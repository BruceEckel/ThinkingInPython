# state_machine.py
from collections.abc import Iterable
from state import State

class StateMachine[I]:
    def __init__(self, initial_state: State[I]) -> None:
        self.current_state = initial_state
        self.current_state.run()
    def step(self, input_: I) -> None:
        state = self.current_state
        self.current_state = state.next(input_)
        print(state, input_, "->", self.current_state)
        self.current_state.run()

def run_all[I](machine: StateMachine[I],
               inputs: Iterable[I]) -> None:
    for input_ in inputs:
        machine.step(input_)
