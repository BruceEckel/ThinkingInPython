# banner_cm.py
from contextlib import ContextDecorator

class banner(ContextDecorator):
    def __init__(self, title: str) -> None:
        self.title = title

    def __enter__(self) -> None:
        print(f"=== {self.title} ===")

    def __exit__(self, *exc: object) -> None:
        print(f"=== {self.title} ends ===")

@banner("quarterly")
def quarterly() -> None:
    print("quarterly numbers")

if __name__ == "__main__":
    quarterly()
    with banner("meeting"):
        print("agenda")
#: === quarterly ===
#: quarterly numbers
#: === quarterly ends ===
#: === meeting ===
#: agenda
#: === meeting ends ===
