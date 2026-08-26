# ch15_ignore_types.py

class ignore:
    def __init__(self, types: type[BaseException] |
                 tuple[type[BaseException], ...]) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object) -> bool:
        if (exc_type is None
            or not issubclass(exc_type, self.types)):
            return False
        print(f"{exc!r}")
        return True

with ignore((ZeroDivisionError, TypeError)):
    print("before")
    raise TypeError("not a number")
print("survived")
#: before
#: TypeError('not a number')
#: survived

with ignore((ZeroDivisionError, TypeError)):
    print("before")
    1 / 0
print("survived")
#: before
#: ZeroDivisionError('division by zero')
#: survived
