# mouse_trap_tables_demo.py
from exceptions import expect
from mouse_action import MouseAction
from mouse_moves import MOVES
from mouse_trap_tables import MouseTrap

MouseTrap().run_all(MOVES)
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse runs away -> Waiting
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse enters trap -> Trapping
#: Closing door
#: Trapping mouse escapes -> Waiting
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse enters trap -> Trapping
#: Closing door
#: Trapping mouse trapped -> Holding
#: Mouse caught
#: Holding mouse removed -> Waiting
#: Broadcasting cheese smell

# ESCAPES is not a key in Waiting.transitions:
trap = MouseTrap()
#: Broadcasting cheese smell
expect(RuntimeError, trap.run_all, [MouseAction.ESCAPES])
#: [RuntimeError] Waiting: no transition on mouse escapes
