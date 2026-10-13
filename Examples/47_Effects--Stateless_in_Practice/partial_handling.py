# partial_handling.py
from exceptions import expected
from greeter import Console
from stateless import Depend, Need, need, run, supply
from stateless.errors import MissingAbilityError

class Log:
    def write(self, entry: str) -> None:
        print(f"log: {entry}")

def work() -> Depend[Need[Console] | Need[Log], None]:
    console = yield from need(Console)
    log = yield from need(Log)
    console.print("working")
    log.write("worked")

half = supply(Console())(work)
with expected(MissingAbilityError):
    run(half())  # type: ignore
#: [MissingAbilityError] Need(t=<class '__main__.Log'>)
