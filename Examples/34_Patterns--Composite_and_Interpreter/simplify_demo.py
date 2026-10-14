# simplify_demo.py
from expr import Num, Var
from infix import to_infix
from simplify import simplify

x = Var("x")
messy = 1 * x + 0 * Var("y") + (Num(2) + 3) * x
print(to_infix(messy))
#: (((1 * x) + (0 * y)) + ((2 + 3) * x))
print(to_infix(simplify(messy)))
#: (x + (5 * x))
