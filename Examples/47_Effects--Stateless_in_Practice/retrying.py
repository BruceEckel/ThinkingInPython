# retrying.py
from datetime import timedelta
from flaky import Crashed, Database, save_user
from stateless import catch, retry, run, supply
from stateless.functions import RetryError
from stateless.schedule import recurs, spaced
from stateless.time import Time

once = catch(Crashed)(save_user)
print(run(supply(Database(failures=2))(once)("Morty")))
#: attempt 1
#: database crashed
three = recurs(3, spaced(timedelta(milliseconds=1)))
retried = retry(three)(save_user)
print(run(
    supply(Database(failures=2), Time())(retried)("Morty")))
#: attempt 1
#: attempt 2
#: attempt 3
#: Morty saved
caught = catch(RetryError)(retried)
outcome = run(
    supply(Database(failures=9), Time())(caught)("Morty"))
#: attempt 1
#: attempt 2
#: attempt 3
match outcome:
    case RetryError():
        print(type(outcome).__name__, len(outcome.args[0]))
#: RetryError 3
