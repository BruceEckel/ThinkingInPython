# error_escapes.py
from announce import announce
from exceptions import expect
from greeter import Console
from stateless import run, supply

expect(KeyError, run, supply(Console())(announce)("Carol"))
#: [KeyError] 'Carol'
