# enter_fails.py

class Fragile:
    def __enter__(self) -> None:
        print("enter fails")
        raise RuntimeError("no resource")

    def __exit__(self, *exc: object) -> bool:
        print("exit runs")
        return False

try:
    with Fragile():
        print("body")
except RuntimeError as error:
    print("caught:", error)
#: enter fails
#: caught: no resource
