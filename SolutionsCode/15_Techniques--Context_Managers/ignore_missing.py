# ignore_missing.py
from types import TracebackType
from exceptions import expected

class ignore_missing:
    def __enter__(self) -> None:
        return None

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> bool:
        return (exc_type is not None
                and issubclass(exc_type, KeyError))

stock = {"apple": 3}

with ignore_missing():
    print(stock["pear"])
    print("never reached")
print("survived the KeyError")
#: survived the KeyError

with expected(ValueError):
    with ignore_missing():
        raise ValueError("not a lookup problem")
#: [ValueError] not a lookup problem
