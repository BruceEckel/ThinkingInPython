# test_mouse_traps.py
import mouse_trap_states
import mouse_trap_tables
import pytest
from mouse_moves import MOVES
from state_machine import run_all

def test_both_versions_print_the_same_trace(
        capsys: pytest.CaptureFixture[str]) -> None:
    run_all(mouse_trap_states.MouseTrap(), MOVES)
    by_match = capsys.readouterr().out
    run_all(mouse_trap_tables.MouseTrap(), MOVES)
    by_table = capsys.readouterr().out
    assert by_match == by_table
