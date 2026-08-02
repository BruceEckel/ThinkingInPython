# catch_subset.py
from read_score import read_score
from stateless import Success, Try, catch, run

both = catch(KeyError, ValueError)(read_score)
one = catch(KeyError)(read_score)

def all_handled(name: str) -> Success[str]:
    value: int | KeyError | ValueError = yield from both(name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case ValueError():
            return f"{name}: unreadable"
        case _:
            return f"{name}: {value}"

def one_left(name: str) -> Try[ValueError, str]:
    value: int | KeyError = yield from one(name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case _:
            return f"{name}: {value}"

for who in ["alice", "bob", "carol"]:
    print(run(all_handled(who)))
#: alice: 42
#: bob: unreadable
#: carol: unknown
print(run(one_left("alice")))
#: alice: 42
try:
    run(one_left("bob"))
except ValueError as e:
    print(type(e).__name__)
#: ValueError
