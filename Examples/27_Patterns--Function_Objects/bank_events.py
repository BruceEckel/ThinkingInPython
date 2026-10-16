# bank_events.py
from tagged_bus import event, handler

@event
class Deposit:
    amount: int

@event
class Withdraw:
    amount: int

@event
class Closed:
    reason: str

@handler
class Announce:
    prefix: str
    def __call__(self, event: Deposit) -> None:
        print(f"{self.prefix} deposit {event.amount}")

@handler
class Audit:
    threshold: int
    def __call__(self, event: Deposit) -> None:
        if event.amount > self.threshold:
            print(f"  audit: large deposit {event.amount}")

@handler
class OnWithdraw:
    def __call__(self, event: Withdraw) -> None:
        print(f"- withdraw {event.amount}")
