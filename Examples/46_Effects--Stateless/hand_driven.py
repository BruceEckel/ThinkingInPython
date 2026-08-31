# hand_driven.py
from greeter import Console, greet

description = greet("Alice")
request = next(description)
print(f"{type(request).__name__}, {request.t.__name__}")
#: Need, Console
try:
    description.send(Console())
except StopIteration:
    print("greet() finished")
#: Hello, Alice!
#: greet() finished
