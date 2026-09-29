# unsupplied.py
from exceptions import expected
from greeter import greet
from stateless import run
from stateless.errors import MissingAbilityError

with expected(MissingAbilityError):
    run(greet("Alice"))  # type: ignore
#: [MissingAbilityError] Need(t=<class 'greeter.Console'>)
