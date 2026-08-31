# microgrid.py
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from power import (
    Backup,
    Battery,
    Drained,
    Grid,
    Outlet,
    Solar,
    Source,
    draw,
    plug,
)
from stateless import Depend, catch, handle, run

class Blackout(Exception):
    pass

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

def run_load(start: int,
             hours: int) -> Depend[Outlet, None]:
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

def site() -> tuple[Solar, Battery, Grid, Backup]:
    return (Solar(), Battery(40), Grid(range(22, 24)),
            Backup(3))

solar, battery, grid, backup = site()
sun_first = controller((solar, battery, grid, backup))
run(handle(sun_first)(run_load)(17, 6))
#: Solar online
#:   17:00
#:   18:00
#: Solar offline
#: Battery online
#:   19:00
#:   20:00
#: Battery offline
#: Grid online
#:   21:00
#: Grid offline
#: Backup online
#:   22:00
#: Backup offline
solar, battery, grid, backup = site()
battery_first = controller((battery, solar, grid, backup))
run(handle(battery_first)(run_load)(17, 4))
#: Battery online
#:   17:00
#:   18:00
#: Battery offline
#: Grid online
#:   19:00
#:   20:00
#: Grid offline
