# late_binding.py
from collections.abc import Callable
from functools import partial

commands: list[Callable[[], None]] = [
    lambda: print(f"step {n}") for n in range(3)
]
for command in commands:
    command()  # Every lambda sees the final n
#: step 2
#: step 2
#: step 2

fixed: list[Callable[[], None]] = [
    partial(print, f"step {n}") for n in range(3)
]
for command in fixed:
    command()
#: step 0
#: step 1
#: step 2
