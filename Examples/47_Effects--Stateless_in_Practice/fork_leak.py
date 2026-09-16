# fork_leak.py
from concurrent.futures import Executor, ThreadPoolExecutor
from exceptions import expect
from stateless import (
    Async,
    Depend,
    Need,
    Try,
    as_type,
    fork,
    run,
    supply,
    throw,
    wait,
)

class Boom(Exception):
    pass

@fork
def bad(n: int) -> Try[Boom, int]:
    yield from throw(Boom(n))
    return 0

def go() -> Depend[Need[Executor] | Async, int]:
    task = yield from bad(1)
    value = yield from wait(task)
    return value

with ThreadPoolExecutor(max_workers=1) as pool:
    supplied = supply(as_type(Executor)(pool))(go)
    expect(Boom, run, supplied())
#: [Boom] 1
