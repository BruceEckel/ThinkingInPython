# closable.py

class Socket:
    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False
        print(name, "opened")

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        print(self.name, "closed")

    def __enter__(self) -> Socket:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

with Socket("A") as sock:
    print("using", sock.name)
sock.close()
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
