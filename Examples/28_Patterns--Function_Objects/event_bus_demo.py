# event_bus_demo.py
from event_bus import Closed, Deposit, EventBus, Withdraw

def on_deposit(event: Deposit) -> None:
    print(f"+ deposit {event.amount}")

def audit(event: Deposit) -> None:
    print(f"  audit: a deposit of {event.amount}")

def on_withdraw(event: Withdraw) -> None:
    print(f"- withdraw {event.amount}")

bus = EventBus()
bus.subscribe(Deposit, on_deposit)
# Two handlers for one event type
bus.subscribe(Deposit, audit)
bus.subscribe(Withdraw, on_withdraw)

bus.publish(Deposit(100))
#: + deposit 100
#:   audit: a deposit of 100
bus.publish(Withdraw(30))
#: - withdraw 30
# No handler: nothing happens
bus.publish(Closed("inactivity"))
