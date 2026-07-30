# reveal_bound.py
from typing import reveal_type
from greeter import Console, greet
from stateless import supply

bound = supply(Console())(greet)
reveal_type(greet)
reveal_type(bound)
