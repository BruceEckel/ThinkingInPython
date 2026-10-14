# trap_tables_demo.py
from exceptions import expect
from mouse import Mouse
from table_state import NoTransition
from trap_tables import MouseTrap

# ESCAPES is not a key in Waiting.transitions:
trap = MouseTrap()
#: Broadcasting cheese smell
expect(NoTransition, trap.step, Mouse.ESCAPES)
#: [NoTransition] Waiting: no transition on mouse escapes
