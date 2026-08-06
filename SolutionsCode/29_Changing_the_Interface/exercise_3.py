# exercise_3.py
import shop
from shop import make_a, make_b

print(make_a(1), make_b(2))
#: _A(x=1) _B(x=2)
print([name for name in vars(shop) if not name.startswith("_")])
#: ['dataclass', 'make_a', 'make_b']
