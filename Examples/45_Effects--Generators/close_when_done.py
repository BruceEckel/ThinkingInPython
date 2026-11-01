# close_when_done.py
import inspect
from collections.abc import Generator

def readings() -> Generator[int]:
    print("sensor on")
    pending = [3, 7, 12, 9, 4]
    try:
        while pending:
            yield pending.pop(0)
    except GeneratorExit:
        print(f"stopped with {len(pending)} unread")
    finally:
        print("sensor off")

def first_above(
    source: Generator[int], limit: int
) -> int | None:
    for reading in source:
        if reading > limit:
            return reading  # [1]
    return None

sensor = readings()
print(first_above(sensor, 10))
#: sensor on
#: 12
print(inspect.getgeneratorstate(sensor))
#: GEN_SUSPENDED
sensor.close()  # [2]
#: stopped with 2 unread
#: sensor off
