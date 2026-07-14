# suppress_cm.py
ALL = sentinel("ALL")
type Types = type[BaseException] | tuple[type[BaseException], ...]

class ignore:
    def __init__(self, types: Types | ALL = ALL) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: object) -> bool:
        if exc_type is None:
            return False
        if self.types is not ALL:
            if not issubclass(exc_type, self.types):
                return False
        print("ignoring", exc_type.__name__)
        return True

with ignore(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")  # Never runs: the error jumps straight to __exit__
print("survived")
#: before
#: ignoring ZeroDivisionError
#: survived

with ignore():  # No argument means ALL
    print("before")
    raise KeyError("anything")
print("survived")
#: before
#: ignoring KeyError
#: survived
