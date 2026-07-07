# Function Objects: Solutions

## 1. Undo, added to `command.py`

```python
# exercise_1.py
class UndoableCommand:
    def execute(self) -> None:
        raise NotImplementedError

    def undo(self) -> None:
        raise NotImplementedError

class Deposit(UndoableCommand):
    def __init__(self, account: dict, amount: int) -> None:
        self.account = account
        self.amount = amount

    def execute(self) -> None:
        self.account["balance"] += self.amount

    def undo(self) -> None:
        self.account["balance"] -= self.amount

class Macro:
    def __init__(self) -> None:
        self.commands: list[UndoableCommand] = []

    def add(self, command: UndoableCommand) -> None:
        self.commands.append(command)

    def run(self) -> None:
        for c in self.commands:
            c.execute()

    def undo_all(self) -> None:
        for c in reversed(self.commands):  # Reverse order to undo
            c.undo()

account = {"balance": 0}
macro = Macro()
macro.add(Deposit(account, 10))
macro.add(Deposit(account, 5))
macro.run()
print(account["balance"])
#: 15
macro.undo_all()
print(account["balance"])
#: 0
```

A bare function is no longer enough. `command.py`'s original `loony`,
`new_brain`, and `afford` take no arguments and remember nothing, so a
plain function fully describes them. Undo needs a command to remember
*what it did*, here the account and the amount deposited, so it can
reverse exactly that action later; a fresh call to the same function
cannot know what a previous call changed. That remembered state is
precisely what an object gives you and a bare function does not. This
confirms the chapter's own line: "the object form earns its keep only
when a command must also carry state or support extra operations such
as undo." Undo is that operation.

## 2. `chain.py`, reporting every attempt

```python
# exercise_2.py
TOLERANCE = 1e-12
MAX_ITER = 200

def bisection(f, a, b):
    if f(a) * f(b) > 0:
        return None
    mid = (a + b) / 2
    for _ in range(MAX_ITER):
        if abs(f(mid)) < TOLERANCE:
            return mid
        if f(a) * f(mid) < 0:
            b = mid
        else:
            a = mid
        mid = (a + b) / 2
    return mid

def secant(f, a, b):
    x0, x1 = a, b
    for _ in range(MAX_ITER):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:
            return None
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < TOLERANCE:
            return x2
        x0, x1 = x1, x2
    return None

def newton(f, a, b):
    x = (a + b) / 2
    h = 1e-7
    for _ in range(MAX_ITER):
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return None
        step = f(x) / slope
        x -= step
        if abs(step) < TOLERANCE:
            return x
    return None

def solve(f, a, b, chain):
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            print(f"{finder.__name__} succeeded: {root:.6f}")
            return root
        print(f"{finder.__name__} failed: could not converge")
    print("all finders failed")
    return None

def f(x):
    return x * x - 2

solve(f, 1.0, 1.3, [bisection, secant, newton])
#: bisection failed: could not converge
#: secant succeeded: 1.414214
```

Each handler function already reports its own outcome through its
return value, `None` for failure, a number for success, so `solve()`
only needs to print that outcome as it checks it, rather than asking
each handler for a separate explanation. `finder.__name__` reads the
function's own name, since every ordinary Python function carries its
name as an attribute, so the report needs no extra bookkeeping to say
*which* handler just ran.

## 3. `sorted()` with a compound key, and why `key` is *Strategy*

```python
# exercise_3.py
scores = [("Bob", 85), ("Amy", 92), ("Cid", 85), ("Amy", 70)]
by_score_then_name = sorted(scores, key=lambda t: (t[1], t[0]))
print(by_score_then_name)
#: [('Amy', 70), ('Bob', 85), ('Cid', 85), ('Amy', 92)]
```

The key function returns a tuple, `(score, name)`, and Python compares
tuples element by element, so `sorted()` orders primarily by score
and, among equal scores (`Bob` and `Cid`, both `85`), falls back to
comparing names. `key` is exactly a *Strategy*: `sorted()` fixes the
*algorithm* (some comparison-based sort), and the caller supplies the
interchangeable *policy* that decides what "in order" means for this
particular call, without `sorted()` itself needing to know anything
about tuples, scores, or names. Passing a different `key` swaps the
ordering strategy the same way `strategy_pattern.py` swaps
`RootSolver`'s algorithm, except here the "context" object holding the
current strategy is just the call to `sorted()` itself.
