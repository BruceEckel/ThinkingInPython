# test_mouse_traps.py
import mouse_trap_states
import mouse_trap_tables
import pytest
from mouse_moves import MOVES

def test_both_versions_print_the_same_trace(
        capsys: pytest.CaptureFixture[str]) -> None:
    mouse_trap_states.MouseTrap().run_all(MOVES)
    by_match = capsys.readouterr().out
    mouse_trap_tables.MouseTrap().run_all(MOVES)
    by_table = capsys.readouterr().out
    assert by_match == by_table
