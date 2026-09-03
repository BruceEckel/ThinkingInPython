# exit_masks.py

class Careless:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *exc: object) -> bool:
        raise ValueError("cleanup error")

try:
    with Careless():
        raise KeyError("original")
except ValueError as error:
    print("caught:", repr(error))
    print("context:", repr(error.__context__))
#: caught: ValueError('cleanup error')
#: context: KeyError('original')
