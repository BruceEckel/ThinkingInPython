# while_loop.py

n = 27
steps = 0
while n != 1:  # The Collatz sequence
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    print(n)
    steps += 1
print(steps, "steps")
