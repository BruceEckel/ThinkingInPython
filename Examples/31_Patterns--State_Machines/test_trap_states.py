# test_trap_states.py
from mouse import Mouse
from mouse_moves import MOVES
from state_machine import StateMachine, run_all
from trap_states import TrapState

def test_nine_moves_return_to_waiting() -> None:
    trap = StateMachine(TrapState.WAITING)
    run_all(trap, MOVES)
    assert trap.current_state is TrapState.WAITING

def test_every_state_answers_every_move() -> None:
    for state in TrapState:
        for move in Mouse:
            assert state.next(move) in TrapState
