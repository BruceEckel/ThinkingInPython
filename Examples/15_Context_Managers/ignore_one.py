# ignore_one.py

class ignore_one:
    def __init__(self, kind: type[BaseException]) -> None:
        self.kind = kind

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object) -> bool:
        if (exc_type is not None
            and issubclass(exc_type, self.kind)):
            print(f"{exc!r}")
            return True
        return False

with ignore_one(ZeroDivisionError):
    print("before")
    1 / 0
    # Never runs: the error jumps to __exit__
    print("after")
print("survived")
#: before
#: ZeroDivisionError('division by zero')
#: survived
