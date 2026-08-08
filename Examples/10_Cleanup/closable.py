# closable.py

class Socket:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")

    def close(self) -> None:
        print(self.name, "closed")

    def __enter__(self) -> Socket:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

with Socket("A") as sock:
    print("using", sock.name)
#: A opened
#: using A
#: A closed
try:
    with Socket("B"):
        raise RuntimeError("boom")
except RuntimeError as e:
    print("caught", e)
#: B opened
#: B closed
#: caught boom
