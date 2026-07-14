# context_decorator.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Iterator[None]:
    print(f"=== {title} ===")
    try:
        yield
    finally:
        print(f"=== {title} ends ===")

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
