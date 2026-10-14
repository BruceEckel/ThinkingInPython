# trap_states_demo.py
from mouse import Mouse
from mouse_moves import MOVES
from state_machine import run_all
from trap_states import MouseTrap

run_all(MouseTrap(), MOVES)
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

# ESCAPES has no case in Waiting, so case _
# fires and the machine stays at Waiting:
trap = MouseTrap()
#: Broadcasting cheese smell
trap.step(Mouse.ESCAPES)
#: Waiting mouse escapes -> Waiting
#: Broadcasting cheese smell
