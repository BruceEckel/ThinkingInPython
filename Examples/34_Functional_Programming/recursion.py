# recursion.py
import sys

def factorial(n: int) -> int:
    # Base case stops the recursion:
    if n <= 1:
        return 1
    # Recursive case moves toward the base case:
    return n * factorial(n - 1)

print(factorial(5))
## 120
# Python caps how deep recursion can go:
print(sys.getrecursionlimit())
## 1000
