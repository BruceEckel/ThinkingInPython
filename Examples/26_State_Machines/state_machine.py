# state_machine.py
from collections.abc import Iterable
from state import State

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    # Template method:
    def run_all(self, inputs: Iterable[object]) -> None:
        for i in inputs:
            print(i)
            self.current_state = self.current_state.next(i)
            self.current_state.run()
