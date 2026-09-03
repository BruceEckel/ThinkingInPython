# faulty_init.py

class Faulty:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        raise RuntimeError("boom")

    def __enter__(self) -> Faulty:
        return self

    def __exit__(self, *exc: object) -> None:
        print(self.name, "closed")

try:
    with Faulty("C"):
        pass
except RuntimeError as e:
    print("caught", e)
#: C opened
#: caught boom
