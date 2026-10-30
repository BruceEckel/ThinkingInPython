# trap_generators_demo.py
from collections.abc import Generator, Iterable
from typing import Final
from trap_generators import Machine, Mouse, waiting

def trampoline(
    state: Machine | None
) -> Generator[str, Mouse]:
    while state is not None:
        state = yield from state  # [1]

def run_all(
    start: Machine, inputs: Iterable[Mouse]
) -> None:
    machine = trampoline(start)
    state = next(machine)  # [2]
    for input_ in inputs:
        new_state = machine.send(input_)  # [3]
        print(state, input_, "->", new_state)
        state = new_state

MOVES: Final[list[Mouse]] = [
    Mouse.APPEARS, Mouse.RUNS_AWAY, Mouse.APPEARS,
    Mouse.ENTERS, Mouse.ESCAPES, Mouse.APPEARS,
    Mouse.ENTERS, Mouse.TRAPPED, Mouse.REMOVED,
]
run_all(waiting(), MOVES)
#: Broadcasting cheese smell
#: Presenting Cheese, door open
#: Waiting mouse appears -> Luring
#: Broadcasting cheese smell
#: Luring mouse runs away -> Waiting
#: Presenting Cheese, door open
#: Waiting mouse appears -> Luring
#: Closing door
#: Luring mouse enters trap -> Trapping
#: Broadcasting cheese smell
#: Trapping mouse escapes -> Waiting
#: Presenting Cheese, door open
#: Waiting mouse appears -> Luring
#: Closing door
#: Luring mouse enters trap -> Trapping
#: Mouse caught
#: *ding*
#: Trapping mouse trapped -> Holding
#: Broadcasting cheese smell
#: Holding mouse removed -> Waiting

trap = trampoline(waiting())
print(next(trap))
#: Broadcasting cheese smell
#: Waiting
print(trap.send(Mouse.ESCAPES))
#: Waiting
