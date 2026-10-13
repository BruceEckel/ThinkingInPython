# null_logger.py
from typing import Final, Protocol
from optional_logger import ListLogger

class Logs(Protocol):
    def log(self, message: str) -> None: ...

class NullLogger:
    def log(self, message: str) -> None:
        pass

SILENT: Final[NullLogger] = NullLogger()

def total(prices: list[float],
          logger: Logs = SILENT) -> float:
    result = 0.0
    for price in prices:
        result += price
        logger.log(f"added {price}, total {result}")
    return result

print(total([1.5, 2.5]))
#: 4.0
logger = ListLogger()
print(total([1.5, 2.5], logger))
#: 4.0
print(logger.lines)
#: ['added 1.5, total 1.5', 'added 2.5, total 4.0']
