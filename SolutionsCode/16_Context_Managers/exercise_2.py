# exercise_2.py
class Ignore:
    def __init__(self, *types) -> None:
        self.types = types

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb) -> bool:
        return (exc_type is not None
                and issubclass(exc_type, self.types))

with Ignore(ZeroDivisionError, TypeError):
    print("before")
    raise TypeError("boom")
print("survived")
#: before
#: survived
