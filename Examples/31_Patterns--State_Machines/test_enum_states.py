# test_enum_states.py
import pytest
import trap_states
from enum_states import TrapState
from mouse_moves import MOVES
from state_machine import StateMachine, run_all

def test_rows_print_the_class_trace(
        capsys: pytest.CaptureFixture[str]) -> None:
    run_all(trap_states.MouseTrap(), MOVES)
    by_class = capsys.readouterr().out
    run_all(StateMachine(TrapState.WAITING), MOVES)
    by_row = capsys.readouterr().out
    assert by_class == by_row
