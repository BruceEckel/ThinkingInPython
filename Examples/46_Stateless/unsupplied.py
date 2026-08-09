# unsupplied.py
from greeter import greet
from stateless import run
from stateless.errors import MissingAbilityError

try:
    run(greet("Alice"))  # type: ignore
except MissingAbilityError as e:
    print(e)
#: Need(t=<class 'greeter.Console'>)
