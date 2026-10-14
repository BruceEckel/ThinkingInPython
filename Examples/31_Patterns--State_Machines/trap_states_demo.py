# trap_states_demo.py
from mouse import Mouse
from mouse_moves import MOVES
from state_machine import StateMachine, run_all
from trap_states import TrapState

run_all(StateMachine(TrapState.WAITING), MOVES)
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

# ESCAPES has no case in waiting(), so case _
# fires and the machine stays at Waiting:
trap = StateMachine(TrapState.WAITING)
#: Broadcasting cheese smell
trap.step(Mouse.ESCAPES)
#: Waiting mouse escapes -> Waiting
#: Broadcasting cheese smell
