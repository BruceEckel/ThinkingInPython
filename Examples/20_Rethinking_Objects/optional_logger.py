# optional_logger.py

class ListLogger:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def log(self, message: str) -> None:
        self.lines.append(message)

def total(prices: list[float],
          logger: ListLogger | None = None) -> float:
    result = 0.0
    for price in prices:
        result += price
        if logger is not None:
            logger.log(f"added {price}, total {result}")
    return result

if __name__ == "__main__":
    print(total([1.5, 2.5]))
    logger = ListLogger()
    print(total([1.5, 2.5], logger), len(logger.lines))
#: 4.0
#: 4.0 2
