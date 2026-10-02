# exercise_7.py

class Faulty:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> Faulty:
        print(self.name, "opened")
        raise RuntimeError("boom")

    def __exit__(self, *exc: object) -> None:
        print(self.name, "closed")

class Guarded:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> Guarded:
        print(self.name, "opened")
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            print(self.name, "closed")
            raise

    def __exit__(self, *exc: object) -> None:
        print(self.name, "closed")

try:
    with Faulty("C"):
        pass
except RuntimeError as e:
    print("caught", e)
#: C opened
#: caught boom
try:
    with Guarded("C"):
        pass
except RuntimeError as e:
    print("caught", e)
#: C opened
#: C closed
#: caught boom
