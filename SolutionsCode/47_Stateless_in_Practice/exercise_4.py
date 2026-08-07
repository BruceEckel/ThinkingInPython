# exercise_4.py
from collections.abc import Callable, Iterator
from grid import Outlet, Solar, Source, run_load
from stateless import handle, run

def scripted(sources: Iterator[Source]) -> Callable[[Outlet], Source]:
    def choose(request: Outlet) -> Source:  # request.hour ignored
        return next(sources)
    return choose

class Dead:  # Never available, so every draw fails
    def available(self, hour: int) -> bool:
        return False
    def deplete(self) -> None:
        pass

sequence = iter([Dead(), Dead(), Solar()])
run(handle(scripted(sequence))(run_load)(10, 2))
#: Dead online
#: Dead offline
#: Dead online
#: Dead offline
#: Solar online
#:   10:00
#:   11:00
#: Solar offline
