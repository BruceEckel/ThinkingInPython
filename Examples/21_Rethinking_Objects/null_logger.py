# null_logger.py
from typing import Final, Protocol

class Logs(Protocol):
    def log(self, message: str) -> None: ...

class NullLogger:
    def log(self, message: str) -> None:
        pass

SILENT: Final[NullLogger] = NullLogger()

class ListLogger:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def log(self, message: str) -> None:
        self.lines.append(message)

def total(prices: list[float],
          logger: Logs = SILENT) -> float:
    result = 0.0
    for price in prices:
        result += price
        logger.log(f"added {price}, total {result}")
    return result

if __name__ == "__main__":
    print(total([1.5, 2.5]))
    logger = ListLogger()
    print(total([1.5, 2.5], logger), len(logger.lines))
#: 4.0
#: 4.0 2
