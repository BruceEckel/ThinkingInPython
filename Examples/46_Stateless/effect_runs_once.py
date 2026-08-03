# effect_runs_once.py
from greeter import Console, greet
from stateless import run, success, supply

bound = supply(Console())(greet)
description = bound("Alice")
run(description)
#: Hello, Alice!
print(repr(run(description)))
#: None
run(bound("Alice"))
#: Hello, Alice!
constant = success(42)
print(run(constant), run(constant))
#: 42 42
