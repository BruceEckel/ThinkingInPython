# Control Flow: Solutions

## 1. `find_factor(97)` and the loop's `else`

```python
# exercise_1.py
def find_factor(n):
    for d in range(2, n):
        if n % d == 0:
            print(f"{n} = {d} * {n // d}")
            break
    else:
        print(f"{n} is prime")

find_factor(97)
#: 97 is prime
```

The loop tries every `d` from 2 up to 96 and never finds a factor, so
it never hits `break`. The `for`'s `else` clause runs exactly when the
loop finishes without a `break`, so it prints `97 is prime`.

## 2. Counting odd steps in the Collatz sequence

```python
# exercise_2.py
def collatz_sequence(n):
    steps = 0
    odd_count = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
            odd_count += 1
        print(n)
        steps += 1
    return steps, odd_count

print(collatz_sequence(10))
#: 5
#: 16
#: 8
#: 4
#: 2
#: 1
#: (6, 1)
```

Six steps total, and only one of them (`5 -> 16`) starts from an odd
`n`. `odd_count` increments in the branch that takes `3 * n + 1`,
which is the branch that only runs when `n` was odd.

## 3. Swapped order of `continue` and `break`

```python
# exercise_3.py
for n in range(10):
    if n == 6:
        break
    if n == 3:
        continue
    print(n, end=" ")
print()
#: 0 1 2 4 5
```

The output is the same as the original order. The two `if`
blocks test different, mutually exclusive values of `n` (`6` and
`3`), so on any given loop iteration at most one of them can be true.
Since neither block's outcome depends on whether the other one ran
first, checking them in either order produces the same result. Order
only matters when two conditions could both be true for the same
value and would send execution down different paths, which is not the
case here.

## 4. A caught exception vs. one that escapes the handler

```python
# exercise_4.py
def checked_divide(a, b):
    if b == 0:
        raise ValueError("Divide by zero")
    return a / b

def demo_exceptions(a, b):
    try:
        checked_divide(a, b)
    except ValueError as e:
        print("caught:", e)
    else:
        print("no exception")
    finally:
        print("finally always runs")

demo_exceptions(1, 2)
#: no exception
#: finally always runs
try:
    demo_exceptions(1, "x")
except TypeError as e:
    print("escaped:", type(e).__name__)
#: finally always runs
#: escaped: TypeError
```

`demo_exceptions(1, 2)` divides cleanly, so `else` runs, then
`finally`. `demo_exceptions(1, "x")` raises `TypeError` inside
`checked_divide` (Python cannot divide an `int` by a `str`), and the
`except` clause only catches `ValueError`. The `finally` block still
runs, because `finally` always runs regardless of what kind of
exception is in flight, but the `TypeError` itself is not caught
there. It keeps propagating up past `demo_exceptions()`, which is why
this listing wraps the call in its own `try`/`except TypeError` to
show the exception actually escaping, the same thing an interactive
session or an outer caller would see.
