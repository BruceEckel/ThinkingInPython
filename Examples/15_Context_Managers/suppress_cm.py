# suppress_cm.py
class Ignore:
    def __init__(self, *types: type[BaseException]) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: object) -> bool:
        return (exc_type is not None
                and issubclass(exc_type, self.types))

with Ignore(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")  # Never runs: the error jumps straight to __exit__
print("survived")
#: before
#: survived
