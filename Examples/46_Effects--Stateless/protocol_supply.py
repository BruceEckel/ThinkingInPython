# protocol_supply.py
from console_protocol import Console, Terminal, greet
from stateless import as_type, run, supply

run(supply(Terminal())(greet)("Alice"))  # type: ignore
#: Hello, Alice!
run(supply(as_type(Console)(Terminal()))(greet)("Bob"))
#: Hello, Bob!
