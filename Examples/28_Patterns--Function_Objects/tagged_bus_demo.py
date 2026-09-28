# tagged_bus_demo.py
from bank_events import (Announce, Audit, Closed,
                         Deposit, OnWithdraw, Withdraw)
from exceptions import expect
from tagged_bus import EventBus

bus = EventBus()
bus.subscribe(Announce("+"))
bus.subscribe(Audit(threshold=50))
bus.subscribe(OnWithdraw())
bus.publish(Deposit(100))
#: + deposit 100
#:   audit: large deposit 100
bus.publish(Deposit(10))
#: + deposit 10
bus.publish(Withdraw(30))
#: - withdraw 30
bus.publish(Closed("inactivity"))  # An event, no handler
expect(TypeError, bus.publish, "Deposit")
#: [TypeError] str is not an @event
