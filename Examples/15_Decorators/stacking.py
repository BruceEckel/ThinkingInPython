# stacking.py
from repeat_class import repeat
from trace_class import trace

@trace
@repeat(times=2)
def greet(name: str) -> str:
    print(f"Hello, {name}")
    return name

if __name__ == "__main__":
    greet("Bob")
#: First deleted
#: 2 Counter objects remaining
#: Second deleted
#: 1 Counter objects remaining
#: Third deleted
#: Last Counter object deleted
#: -> greet('Bob',)
#: Hello, Bob
#: Hello, Bob
#: <- greet = 'Bob'
