# grid.py
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Protocol
from stateless import Ability, Depend, catch, throws

class Drained(Exception):
    pass

class Blackout(Exception):
    pass

class Source(Protocol):
    def available(self, hour: int) -> bool: ...
    def deplete(self) -> None: ...

class Solar:
    def available(self, hour: int) -> bool:
        return 6 <= hour < 19
    def deplete(self) -> None:
        pass

@dataclass
class Turbine:
    windy: range
    def available(self, hour: int) -> bool:
        return hour in self.windy
    def deplete(self) -> None:
        pass

@dataclass
class Battery:
    charge: int
    def available(self, hour: int) -> bool:
        return self.charge >= 20
    def deplete(self) -> None:
        self.charge -= 20

@dataclass
class Grid:
    outage: range
    def available(self, hour: int) -> bool:
        return hour not in self.outage
    def deplete(self) -> None:
        pass

@dataclass
class Backup:
    fuel: int
    def available(self, hour: int) -> bool:
        return self.fuel > 0
    def deplete(self) -> None:
        self.fuel -= 1

@dataclass(frozen=True)
class Outlet(Ability[Source]):
    hour: int

def plug(hour: int) -> Depend[Outlet, Source]:
    source: Source = yield from Outlet(hour)
    return source

@throws(Drained)
def draw(source: Source, hour: int) -> None:
    if not source.available(hour):
        raise Drained(type(source).__name__)
    source.deplete()

def controller(
    order: tuple[Source, ...],
) -> Callable[[Outlet], Source]:
    def choose(request: Outlet) -> Source:
        for source in order:
            if source.available(request.hour):
                return source
        raise Blackout(request.hour)
    return choose

@contextmanager
def connected(source: Source) -> Iterator[Source]:
    name = type(source).__name__
    print(f"{name} online")
    try:
        yield source
    finally:
        print(f"{name} offline")

def run_load(
    start: int, hours: int
) -> Depend[Outlet, None]:
    caught = catch(Drained)
    hour, remaining = start, hours
    while remaining:
        source = yield from plug(hour)
        with connected(source) as power:
            while remaining:
                failure = yield from caught(draw)(
                    power, hour)
                if failure is not None:
                    break
                print(f"  {hour}:00")
                hour += 1
                remaining -= 1
