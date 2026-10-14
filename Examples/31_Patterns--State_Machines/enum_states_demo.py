# enum_states_demo.py
from enum_states import MouseTrap, StateMachine
from mouse_moves import MOVES

machine = StateMachine(MouseTrap.WAITING)
for move in MOVES:
    before = machine.state
    result = machine.output(move)
    print(before.name, move, "->", machine.state.name)
    print("   ", result)
#: WAITING mouse appears -> LURING
#:     Broadcasting cheese smell
#: LURING mouse runs away -> WAITING
#:     Presenting Cheese, door open
#: WAITING mouse appears -> LURING
#:     Broadcasting cheese smell
#: LURING mouse enters trap -> TRAPPING
#:     Presenting Cheese, door open
#: TRAPPING mouse escapes -> WAITING
#:     Closing door
#: WAITING mouse appears -> LURING
#:     Broadcasting cheese smell
#: LURING mouse enters trap -> TRAPPING
#:     Presenting Cheese, door open
#: TRAPPING mouse trapped -> HOLDING
#:     Closing door
#: HOLDING mouse removed -> WAITING
#:     Mouse caught
