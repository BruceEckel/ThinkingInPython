# stacking.py
from repeat import repeat
from tracer import trace

@trace
@repeat(times=2)
def greet(name: str) -> str:
    print(f"Hello, {name}")
    return name

if __name__ == "__main__":
    greet("Bob")
#: -> greet('Bob')
#: Hello, Bob
#: Hello, Bob
#: <- greet = 'Bob'
