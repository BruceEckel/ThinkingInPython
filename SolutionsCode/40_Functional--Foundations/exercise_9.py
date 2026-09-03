# exercise_9.py
from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial

@dataclass(frozen=True)
class Reading:
    sensor: str
    celsius: float

def warmer_than(limit: float, r: Reading) -> bool:
    return r.celsius > limit

def colder_than(limit: float, r: Reading) -> bool:
    return r.celsius < limit

def to_fahrenheit(r: Reading) -> Reading:
    return Reading(r.sensor, r.celsius * 9 / 5 + 32)

def report(readings: Sequence[Reading]) -> list[str]:
    warm = filter(partial(warmer_than, 20.0), readings)
    band = filter(partial(colder_than, 30.0), warm)
    return [f"{r.sensor} {r.celsius:.1f}"
            for r in map(to_fahrenheit, band)]

def converted_first(
    readings: Sequence[Reading],
) -> list[str]:
    hot = map(to_fahrenheit, readings)
    warm = filter(partial(warmer_than, 20.0), hot)
    band = filter(partial(colder_than, 30.0), warm)
    return [f"{r.sensor} {r.celsius:.1f}" for r in band]

data = [Reading("a", 18.0), Reading("b", 25.0),
        Reading("c", 30.5)]
print(report(data))
#: ['b 77.0']
print(converted_first(data))
#: []
print([r.celsius for r in data])
#: [18.0, 25.0, 30.5]
