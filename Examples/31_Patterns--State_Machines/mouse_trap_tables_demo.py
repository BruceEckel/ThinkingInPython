# mouse_trap_tables_demo.py
from exceptions import expect
from mouse import Mouse
from mouse_trap_tables import MouseTrap
from table_state import NoTransition

# ESCAPES is not a key in Waiting.transitions:
trap = MouseTrap()
#: Broadcasting cheese smell
expect(NoTransition, trap.step, Mouse.ESCAPES)
#: [NoTransition] Waiting: no transition on mouse escapes
