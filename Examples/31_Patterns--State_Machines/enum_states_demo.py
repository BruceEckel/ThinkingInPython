# enum_states_demo.py
from enum_states import StateMachine, TrapState
from mouse_moves import MOVES

machine = StateMachine(TrapState.WAITING)
for move in MOVES:
    before = machine.state
    result = machine.step(move)
    print(before.name, move, "->", machine.state.name)
    print("   ", result)
#: WAITING mouse appears -> LURING
#:     Presenting Cheese, door open
#: LURING mouse runs away -> WAITING
#:     Broadcasting cheese smell
#: WAITING mouse appears -> LURING
#:     Presenting Cheese, door open
#: LURING mouse enters trap -> TRAPPING
#:     Closing door
#: TRAPPING mouse escapes -> WAITING
#:     Broadcasting cheese smell
#: WAITING mouse appears -> LURING
#:     Presenting Cheese, door open
#: LURING mouse enters trap -> TRAPPING
#:     Closing door
#: TRAPPING mouse trapped -> HOLDING
#:     Mouse caught
#: HOLDING mouse removed -> WAITING
#:     Broadcasting cheese smell
