# banner_cm.py
from contextlib import ContextDecorator

class banner(ContextDecorator):
    def __init__(self, title: str) -> None:
        self.title = title

    def __enter__(self) -> None:
        print(f"=== {self.title} ===")

    def __exit__(self, *exc: object) -> bool:
        print(f"=== {self.title} ends ===")
        return False

@banner("report")
def report() -> None:
    print("quarterly numbers")

if __name__ == "__main__":
    report()
    with banner("meeting"):
        print("agenda")
#: === report ===
#: quarterly numbers
#: === report ends ===
#: === meeting ===
#: agenda
#: === meeting ends ===
