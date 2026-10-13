# recursion.py
from exceptions import expect

def factorial(n: int) -> int:
    # Base case stops the recursion:
    if n <= 1:
        return 1
    # Recursive case moves toward the base case:
    return n * factorial(n - 1)

print(factorial(5))
#: 120
expect(RecursionError, factorial, 5000)
#: [RecursionError] maximum recursion depth exceeded
