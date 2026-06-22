# Testing

One of the most valuable habits in modern programming is unit testing.
You build tests into the code you write and run them on every change.
It is as if you extend the language to determine if the code means what you intended.

Unit testing is a development practice.
Tests give you a safety net.
With them you can refactor boldly, change designs, and clean up code.

Perhaps more importantly, tests tell you immediately if a change you've made causes a failure.
This can save an enormous amount of time compared to discovering a problem after many more changes to the code,
at which point you don't have any idea *which* change caused the bug.

## Test-Driven Development (TDD)

It seems easy to write the code, get it working,
and intend to write the tests later.
Later rarely comes.
The tests seem to lose their importance.

One solution is to write the tests *before* writing the code.
When you write the tests first, you:

1.  Describe what the code should do, in concrete and verifiable terms,
    not in a separate document that drifts out of date.
2.  Provide a worked example of how the code is meant to be used.
3.  Get a clear definition of done: the code is finished when the tests pass.

Testing then becomes a design tool,
not a verification step you skip when you happen to feel good about the code you just wrote.

That said, TDD requires that you know what you are creating.
You are confident the design is correct, and it is now a matter of implementation.
You need that certainty in order to write tests first.
Often, however, you are not sure what direction a program will take you.
You are experimenting to see what the right approach is.
When you are not simply producing code, but discovering your design, TDD is wasteful.
Writing tests for exploratory programming is not practical.
With the advent of AI, generating tests once you have found a good path becomes far more viable.
It also makes it easier to produce a more thorough test suite.

## pytest

Python has a testing framework in the standard library, `unittest`,
modeled on Java's JUnit.
It works, but it carries the class-based boilerplate of its heritage.
The wider Python world has settled on `pytest`, and so does this book.

`pytest` is built around two ideas that keep tests short.
A test is just a function whose name starts with `test_`.
A check is just Python's built-in `assert` statement.
There is no base class to inherit and no special assertion methods to memorize.
`pytest` rewrites `assert` so that a failure still shows you both sides of the comparison.

We will test the following:

```python
# account.py

class InsufficientFunds(Exception):
    def __init__(self, balance: float, amount: float) -> None:
        super().__init__(f"balance {balance} is less than {amount}")

class Account:
    def __init__(self, balance: float = 0.0) -> None:
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise InsufficientFunds(self.balance, amount)
        self.balance -= amount

    def add_interest(self, rate: float) -> None:
        self.balance += self.balance * rate
```

By convention, tests live in a file whose name starts with `test_`:

```python
# test_account.py
import pytest
from account import Account, InsufficientFunds

def test_new_account_is_empty() -> None:
    assert Account().balance == 0.0

def test_deposit_increases_balance() -> None:
    account = Account()
    account.deposit(100)
    assert account.balance == 100

# Make three tests, replacing "bad" with each list value:
@pytest.mark.parametrize("bad", [0, -1, -100])
def test_nonpositive_deposit_raises(bad: float) -> None:
    with pytest.raises(ValueError):
        Account().deposit(bad)

@pytest.fixture
def funded() -> Account:
    account = Account()
    account.deposit(100)
    return account

def test_withdraw_reduces_balance(funded: Account) -> None:
    funded.withdraw(40)
    assert funded.balance == 60

def test_overdraft_raises(funded: Account) -> None:
    with pytest.raises(InsufficientFunds):
        funded.withdraw(1000)

def test_interest_uses_approx(funded: Account) -> None:
    funded.add_interest(0.05)
    assert funded.balance == pytest.approx(105.0)
```

Run the test suite by typing `pytest` in the project.
It discovers every `test_*.py` file, collects every `test_` function, runs them,
and reports success and failures.
A failing `assert` prints the expression and the actual values,
so you rarely need a debugger to see what went wrong.

## Testing for Exceptions and Floating Point

There are two common special needs in testing, both of which appear in `test_account.py`.

The first is "this call should cause an exception."
`test_overdraft_raises` uses `pytest.raises` as a context manager.
The test passes only if the expected exception is raised inside the block.

The second is comparing floating-point numbers, where exact equality is a trap.
`test_interest_uses_approx` compares with `pytest.approx`,
which allows a small tolerance.

## Parametrizing Tests

When the same logic should run against several inputs, do not copy the test.
Mark it with `parametrize`, as `test_nonpositive_deposit_raises` does,
and `pytest` runs it once per case, reporting each separately.
That single function becomes three independent tests,
and a failure names the exact case that failed.

You are not limited to one variable;
you can give `parametrize` several names and a list of tuples, one tuple per case:

```python
# test_balances.py
import pytest
from account import Account

@pytest.mark.parametrize("start, spend, expected", [
    (100, 40, 60),
    (50, 50, 0),
    (200, 1, 199),
])
def test_withdraw_leaves_expected_balance(
    start: float, spend: float, expected: float
) -> None:
    account = Account(start)
    account.withdraw(spend)
    assert account.balance == expected
```

Each tuple supplies all three arguments for one run,
so this produces three independent tests.
The names in the string line up, in order, with the values in each tuple.

## Fixtures Replace Setup and Teardown

JUnit-style frameworks give each test class a `setUp()` and `tearDown()`.
`pytest` replaces both with *fixtures*: functions that build what a test needs.
These fixtures are declared as parameters to the test functions,
which tells `pytest` to automatically call the fixture function and pass its result to the test function.

The `funded` function in `test_account.py` is a fixture.
A test that names `funded` as an argument receives the value the fixture returns.

Each test gets its own freshly built `funded` account,
so tests cannot leak state into each other.
If a fixture needs cleanup,
it can `yield` the value and run teardown code after the `yield`.
For example, this fixture builds an account, `yield`s it to the test,
then runs teardown once the test returns:

```python
# test_teardown.py
from collections.abc import Iterator
import pytest
from account import Account

@pytest.fixture
def open_account() -> Iterator[Account]:
    account = Account()
    account.deposit(100)  # Setup, before the yield
    yield account  # The test runs with this value
    account.withdraw(account.balance)  # Teardown, after the test
    assert account.balance == 0

def test_spend_some(open_account: Account) -> None:
    open_account.withdraw(30)
    assert open_account.balance == 70
```

Everything before the `yield` is setup.
Everything after it runs once the test finishes, even if the test failed.
After the `yield` is the place to close files, release locks, or check a final invariant.

You can automatically invoke a fixture for every test (without specifying the fixture in each test)
by adding the `autouse` flag:

    @pytest.fixture(autouse=True)

Fixtures are powerful and prevent a lot of duplicated code.
Less code generally makes tests easier to read and verify.

## Sharing Fixtures with conftest.py

A fixture defined in a file named `conftest.py` is available to every test in that directory and below,
with no import.
This is where shared setup lives.

Parameterization can also be applied to fixtures.
Every test that requests the fixture runs once for each parameter value:

```python
# conftest.py
import pytest
from account import Account

@pytest.fixture(scope="session")
def bank_name() -> str:
    "Built once for the whole test session."
    return "Crunchy Frog Credit Union"

@pytest.fixture(params=[0.0, 100.0, 1_000_000.0])
def preloaded(request: pytest.FixtureRequest) -> Account:
    "Parametrized over starting balances; tests run once per value."
    return Account(request.param)
```

The `scope="session"` fixture is built once and reused,
which is useful for expensive resources.
The `preloaded` fixture is rebuilt for each parameter,
so a test that uses it is automatically checked at every starting balance:

```python
# test_fixtures.py
from account import Account

def test_deposit_on_any_balance(
    preloaded: Account, bank_name: str
) -> None:
    start = preloaded.balance
    preloaded.deposit(1)
    assert preloaded.balance == start + 1
    assert bank_name  # The session fixture is available everywhere
```

Neither fixture is imported.
`pytest` finds them in `conftest.py` and supplies them by name.

## Isolating Tests from the World

Good tests do not depend on the real filesystem, clock, network, or environment.
`pytest` ships built-in fixtures for this.
`tmp_path` gives each test a private temporary directory.
`monkeypatch` sets and restores environment variables and attributes,
undoing every change when the test ends.

### File System & Environment

This example reads an environment variable and touches files:

```python
# storage.py
import os
from pathlib import Path

def data_dir() -> Path:
    return Path(os.environ.get("APP_DATA", "."))

def save(name: str, value: str) -> None:
    (data_dir() / name).write_text(value, encoding="utf-8")

def load(name: str) -> str:
    return (data_dir() / name).read_text(encoding="utf-8")
```

The tests redirect it at a throwaway directory,
so they never touch real data and never collide with each other:

```python
# test_storage.py
from pathlib import Path
import pytest
import storage

def test_round_trip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    storage.save("greeting.txt", "hello")
    assert storage.load("greeting.txt") == "hello"

def test_missing_file_raises(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        storage.load("absent.txt")
```

### Random Numbers

Code that calls `random` produces a different value each run,
which a test cannot assert against:

```python
# dice.py
import random

def roll() -> int:
    return random.randint(1, 6)
```

`monkeypatch` replaces the random call with one that returns a known value,
so the result is predictable for the duration of the test:

```python
# test_dice.py
import dice
import pytest

def test_roll_returns_known_value(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(dice.random, "randint", lambda a, b: 4)
    assert dice.roll() == 4
```

Patching the function gives you the exact value you want.

Seeding the generator with `random.seed(0)` makes the sequence repeatable,
though you must record the values it produces rather than choose them.
Better still, have the code accept a `random.Random` instance,
so a test passes a seeded `random.Random(0)` and needs no patching at all:

```python
# dice_rng.py
import random

def roll(rng: random.Random) -> int:
    return rng.randint(1, 6)
```

```python
# test_dice_rng.py
import random
import dice_rng

def test_roll_with_seeded_rng() -> None:
    assert dice_rng.roll(random.Random(0)) == 4
```

The function takes its source of randomness as an argument,
so production code hands it a fresh `random.Random()` while the test hands it a
seeded one. The randomness is now an input, not a hidden dependency.

### Reading the Clock

Code that reads `time.time()` gives a different answer every run:

```python
# stopwatch.py
import time

def elapsed(start: float) -> float:
    return time.time() - start
```

`monkeypatch` pins it to a fixed value the same way it did for `randint`:

```python
# test_stopwatch.py
import time
import pytest
import stopwatch

def test_elapsed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "time", lambda: 100.0)
    assert stopwatch.elapsed(40.0) == 60.0
```

As with randomness, injecting the clock is cleaner still.
The `stamp` function takes a `now` callable:

```python
# clock.py
from collections.abc import Callable

def stamp(now: Callable[[], float]) -> float:
    return now()
```

In the test we can easily provide a fixed value for `now`:

```python
# test_clock.py
import clock

def test_stamp() -> None:
    assert clock.stamp(lambda: 100.0) == 100.0
```

`datetime.now()` is harder to patch, because `datetime` is a built-in type,
so the injection approach is worth the small effort.

If you cannot change the code, the library
[`time-machine`](https://github.com/adamchainz/time-machine) freezes every clock at once,
including `datetime.now()`, with no monkeypatching on your part:

```python
# event.py
from datetime import datetime

def current_year() -> int:
    return datetime.now().year
```

```python
# test_event.py
import event
import time_machine

@time_machine.travel("2030-06-15", tick=False)
def test_current_year_is_frozen() -> None:
    assert event.current_year() == 2030
```

`travel` sets the clock to the given moment for the test,
and `tick=False` holds it there so every reading is identical.
Unlike the prior tools it is a third-party dependency,
but it is the standard answer for code already steeped in `datetime`.

### Network Calls



## White-Box and Black-Box Tests

A *white-box* test reaches into the internals of the code it checks.
A *black-box* test treats the code as an opaque box and exercises only its public interface,
the way a client would.

In a language with access control, the two are enforced differently.
Python has no access control.
Every attribute is reachable,
and a leading underscore is only a convention that says,
"this is private, do not rely on it."
In Python the distinction is one of discipline, not of compiler enforcement.

That makes black-box testing the sensible default.
Test the public surface, the methods a caller is meant to use,
and you stay free to change the internals without rewriting the tests.
The `Account` tests are black-box: they never read a private attribute.
When you do need a white-box test for a tricky internal, nothing stops you,
but treat each one as a test that may break when you refactor.

## How This Book Runs Its Tests

The examples in this book are extracted from the chapters and checked automatically.
Plain programs are run, and their failures are reported.
Files named `test_*.py` and `conftest.py` are handed to `pytest` instead,
and a failing test fails the build.

## Exercises

1.  Add a `transfer(other, amount)` method to `Account` and write its tests first:
    a successful transfer, and an overdraft that leaves both accounts unchanged.
2.  Use `parametrize` to test `add_interest` at several rates,
    comparing with `pytest.approx`.
3.  Write a fixture that `yield`s an `Account` and asserts, after the `yield`,
    that the balance is never negative.
    Use it in two tests.
