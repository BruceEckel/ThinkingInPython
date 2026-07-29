# effect_by_hand.py
from greeter import Console, greet

effect = greet("Alice")
request = next(effect)
print(f"{type(request).__name__}({request.t.__name__})")
#: Need(Console)
try:
    effect.send(Console())
except StopIteration:
    print("returned")
#: Hello, Alice!
#: returned
