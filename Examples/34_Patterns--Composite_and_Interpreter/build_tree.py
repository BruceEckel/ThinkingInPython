# build_tree.py
from expr import Add, Mul, Num, Var

x = Var("x")
expr = 2 * x + 1
nested = Add(Mul(Num(2), x), Num(1))
print(expr == nested, type(expr).__name__, expr.left)
#: True Add Mul(left=Num(value=2), right=Var(name='x'))
