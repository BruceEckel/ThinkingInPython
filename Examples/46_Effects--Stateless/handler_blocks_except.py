# handler_blocks_except.py
from except_vs_catch import guarded
from exceptions import expect
from greeter import Console
from stateless import run, supply

expect(KeyError, run, supply(Console())(guarded)("Carol"))
#: [KeyError] 'Carol'
