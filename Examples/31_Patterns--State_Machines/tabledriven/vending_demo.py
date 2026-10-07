# tabledriven/vending_demo.py
from vending_machine import (FirstDigit, Money, Quit,
                             SecondDigit, VendingMachine)

events = [
    Money("quarter", 25), Money("quarter", 25),
    Money("dollar", 100),
    # Buy [0][1]
    FirstDigit("A", 0), SecondDigit("col 1", 1),
    # Buy it again
    FirstDigit("A", 0), SecondDigit("col 1", 1),
    # Too expensive
    FirstDigit("C", 2), SecondDigit("col 2", 2),
    # Sold out
    FirstDigit("D", 3), SecondDigit("col 0", 0),
    Quit(),  # Refund and reset
    # Row D, col 0 is both too expensive (a dime
    # isn't 25 cents) and sold out (quantity 0);
    # too_expensive is listed first, so it wins:
    Money("dime", 10),
    FirstDigit("D", 3), SecondDigit("col 0", 0),
]
machine = VendingMachine()
for event in events:
    machine.handle(event)
    print(f"{event}: {machine.message} "
          f"[{machine.state.name}]")
#: quarter: Total = 25 [COLLECTING]
#: quarter: Total = 50 [COLLECTING]
#: dollar: Total = 150 [COLLECTING]
#: A: Row A [SELECTING]
#: col 1: Dispensing; remaining 100 [WANT_MORE]
#: A: Row A [SELECTING]
#: col 1: Dispensing; remaining 50 [WANT_MORE]
#: C: Row C [SELECTING]
#: col 2: Cleared: costs 75, quantity 5 [COLLECTING]
#: D: Row D [SELECTING]
#: col 0: Cleared: costs 25, quantity 0 [UNAVAILABLE]
#: Quit: Returning 50 [QUIESCENT]
#: dime: Total = 10 [COLLECTING]
#: D: Row D [SELECTING]
#: col 0: Cleared: costs 25, quantity 0 [COLLECTING]
