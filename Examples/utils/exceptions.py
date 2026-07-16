# utils/exceptions.py

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
        print(f"{exc!r}")
        return True
