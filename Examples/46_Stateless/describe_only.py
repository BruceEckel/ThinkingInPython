# describe_only.py
from greeter import greet

description = greet("Alice")
print(type(description).__name__)
#: generator
