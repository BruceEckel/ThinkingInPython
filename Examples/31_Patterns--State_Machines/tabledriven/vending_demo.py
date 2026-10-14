# tabledriven/vending_demo.py
from vending_machine import (Column, Money, Quit, Row,
                             VendingMachine)

inputs = [
    Money("quarter", 25), Money("quarter", 25),
    Money("dollar", 100),
    # Buy [0][1]
    Row.A, Column(1),
    # Buy it again
    Row.A, Column(1),
    # Too expensive
    Row.C, Column(2),
    # Sold out
    Row.D, Column(0),
    Quit(),  # Refund and reset
    # Row D, col 0 is both too expensive (a dime
    # isn't 25 cents) and sold out (quantity 0);
    # too_expensive is listed first, so it wins:
    Money("dime", 10),
    Row.D, Column(0),
]
machine = VendingMachine()
for input_ in inputs:
    before = machine.state
    machine.handle(input_)
    print(f"{before.name} {input_} -> "
          f"{machine.state.name}: {machine.message}")
#: QUIESCENT quarter -> COLLECTING: Total = 25
#: COLLECTING quarter -> COLLECTING: Total = 50
#: COLLECTING dollar -> COLLECTING: Total = 150
#: COLLECTING A -> SELECTING: 25c to 100c
#: SELECTING col 1 -> WANT_MORE: Dispensing; remaining 100
#: WANT_MORE A -> SELECTING: 25c to 100c
#: SELECTING col 1 -> WANT_MORE: Dispensing; remaining 50
#: WANT_MORE C -> SELECTING: 25c to 100c
#: SELECTING col 2 -> COLLECTING: Cleared: 75c, 5 left
#: COLLECTING D -> SELECTING: 25c to 100c
#: SELECTING col 0 -> UNAVAILABLE: Cleared: 25c, 0 left
#: UNAVAILABLE Quit -> QUIESCENT: Returning 50
#: QUIESCENT dime -> COLLECTING: Total = 10
#: COLLECTING D -> SELECTING: 25c to 100c
#: SELECTING col 0 -> COLLECTING: Cleared: 25c, 0 left
