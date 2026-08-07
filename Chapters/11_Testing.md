# Testing

One of the most valuable habits in modern programming is unit testing.
You build tests into the code you write and run them on every change.
A type checker verifies the claims you can write as annotations.
Tests verify the rest: that a withdrawal reduces the balance,
that an overdraft is refused.
They state what the code is supposed to do, and check it.

Tests give you a safety net.
With them you can refactor boldly, change designs, and clean up code.

Perhaps more importantly,
tests tell you immediately if a change you've made causes a failure.
This can save an enormous amount of time.
If the problem only surfaces after multiple changes,
you have no idea which change caused the bug.

## Test-Driven Development (TDD)

It seems easy to write the code, get it working,
and intend to write the tests later.
Later rarely comes.
The tests seem to lose their importance.

One solution is to write the tests before writing the code.
When you write the tests first, you:

1.  Describe what the code should do, in concrete and verifiable terms,
    not in a separate document that drifts out of date.
2.  Provide a worked example of how to use the code.
3.  Get a clear definition of done: the code is finished when the tests pass.

Testing then becomes a design tool,
not a verification step you skip when the code looks right to you.

That said, TDD requires that you know what you are creating.
It assumes you are confident the design is correct,
so that only implementation remains.
Often, however, you are not sure what direction a program will take you.
You are experimenting to look for the correct approach.
When you are not simply producing code, but discovering your design,
TDD is wasteful.
Once you have found a good path,
AI makes a thorough test suite far cheaper to produce.

## pytest

Python has a testing framework in the standard library, `unittest`,
modeled on Java's JUnit.
It works, but it carries the class-based boilerplate of its heritage.
The wider Python world has settled on `pytest`, and so does this book.

`pytest` rests on two ideas that keep tests short.
A test is just a function whose name starts with `test_`.
A check is just Python's built-in `assert` statement.
No base class needs inheriting,
and no special assertion methods need memorizing.
`pytest` rewrites `assert` so that a failure still shows you both sides of the comparison.

The tests that follow check the `Account` class:

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

# Make three tests, replacing "bad" with each list value
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

Run the test suite by typing `pytest` in the project directory.
`pytest` puts each test file's own directory at the front of `sys.path`,
which is why `from account import Account` works with no packaging and no path setup,
as long as `account.py` sits beside `test_account.py`.
It discovers every `test_*.py` file, collects every `test_` function, runs them,
and reports success and failures.
A failing `assert` prints the expression and the actual values,
so you rarely need a debugger to see what went wrong.

Change the expected value in `test_deposit_increases_balance()` to `10` and the report names the line,
the expression, and both sides:

```text
______________ test_deposit_increases_balance ______________

    def test_deposit_increases_balance() -> None:
        account = Account()
        account.deposit(100)
>       assert account.balance == 10
E       assert 100.0 == 10
E        +  where 100.0 = <account.Account object>.balance

test_account.py:6: AssertionError
```

The `where` line is the rewriting at work:
`pytest` kept the sub-expression `account.balance` and its value,
which a bare `assert` statement would have discarded.

## Testing for Exceptions and Floating Point

Two situations come up repeatedly in testing,
and both appear in `test_account.py`.

The first is "this call should raise an exception."
`test_overdraft_raises()` uses `pytest.raises()` as a context manager.
The test passes only if the block raises the expected exception.

Keep the `with` block down to the single call that should fail.
Any statement inside it that raises the expected type passes the test,
including one that fails for an unrelated reason.
`match=` takes a regular expression checked against the exception's message,
so the test can confirm which failure occurred and not just its type:

```python
# test_overdraft_message.py
import pytest
from account import Account, InsufficientFunds

def test_overdraft_reports_the_shortfall() -> None:
    account = Account(100)
    with pytest.raises(InsufficientFunds, match="less than 250"):
        account.withdraw(250)
    assert account.balance == 100
```

The assertion after the block belongs outside it:
a failed withdrawal must leave the balance alone,
and that check has nothing to do with the exception.

The second is comparing floating-point numbers,
where testing for exact equality is unreliable.
`test_interest_uses_approx()` compares with `pytest.approx()`,
which allows a small tolerance.

## Parametrizing Tests

When the same logic should run against several inputs, do not copy the test.
If you mark it with `parametrize`, as `test_nonpositive_deposit_raises()` does,
`pytest` runs it once per case and reports each separately.
That single function becomes three independent tests,
and a failure names the case that failed.

Nothing limits you to one variable.
You can give `parametrize` several names and a list of tuples,
one tuple per case:

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
You declare fixtures as parameters to a test,
which tells `pytest` to call the fixture and pass its result to the test.

The `funded` function in `test_account.py` is a fixture.

Each test gets its own freshly built `funded` account,
so tests cannot leak state into each other.
If a fixture needs cleanup,
it can `yield` the value and run teardown code after the `yield`.
For example:

```python
# test_teardown.py
from collections.abc import Iterator
import pytest
from account import Account

@pytest.fixture
def open_account() -> Iterator[Account]:
    account = Account()
    account.deposit(100)
    yield account
    account.withdraw(account.balance)
    assert account.balance == 0

def test_spend_some(open_account: Account) -> None:
    open_account.withdraw(30)
    assert open_account.balance == 70
```

Everything before the `yield` is setup.
Everything after it runs once the test finishes, even if the test failed.
After the `yield` is the place to close files, release locks,
or check a final invariant.

You can automatically invoke a fixture for every test
(without specifying the fixture in each test) by adding the `autouse` flag:

    @pytest.fixture(autouse=True)

Fixtures eliminate duplicated setup.
A test that names `funded` states what it needs and nothing about how to build it.

## Sharing Fixtures with conftest.py

A fixture defined in a file named `conftest.py` is available to every test in that directory and below,
with no import.
Place shared setup in `conftest.py`.

You can parameterize fixtures too.
Every test that requests the fixture runs once for each parameter value:

```python
# conftest.py
import pytest
from account import Account

@pytest.fixture(scope="session")
def bank_name() -> str:
    return "Crunchy Frog Credit Union"

@pytest.fixture(params=[0.0, 100.0, 1_000_000.0])
def preloaded(request: pytest.FixtureRequest) -> Account:
    return Account(request.param)
```

`pytest` builds the `scope="session"` fixture once and reuses it,
which is useful for expensive resources.
The reuse is the risk as well as the point: every test receives the same object,
so one test that mutates it changes what the next test sees.
Keep session fixtures to values nothing modifies, like `bank_name`,
or to a resource with its own reset,
and leave anything a test writes to at the default per-test scope.
`pytest` rebuilds the `preloaded` fixture for each parameter,
so a test that uses it automatically runs at every starting balance:

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

Nothing imports either fixture.
`pytest` finds them in `conftest.py` and supplies them by name.

## Isolating Tests from the World

Good tests do not depend on the real filesystem, environment,
random number generation, clock, or network.
`pytest` includes built-in fixtures for this.
`tmp_path` gives each test a private temporary directory.
`monkeypatch` sets and restores environment variables and attributes,
undoing every change when the test ends.

### Filesystem and Environment

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

The tests point it at a throwaway directory,
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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

`import random` binds the one module object every importer shares,
so `dice.random` and `random` are the same object and the patch replaces `randint()` process-wide.
`monkeypatch` restores the original when the test ends,
which is what keeps that safe.

Seeding the generator with `random.seed(0)` makes the sequence repeatable,
though you must record the values it produces rather than choose them.
Better still, have the code accept a `random.Random` instance,
so a test passes a seeded `random.Random(0)` and needs no patching:

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
so production code hands it a fresh `random.Random()` while the test hands it a seeded one.
The randomness is now an input, not a hidden dependency.

### The Clock

Code that reads `time.time()` gives a different answer every run:

```python
# stopwatch.py
import time

def elapsed(start: float) -> float:
    return time.time() - start
```

`monkeypatch` pins it to a fixed value the same way it did for `randint()`:

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
The `stamp()` function takes a `now` callable:

```python
# clock.py
from collections.abc import Callable

def stamp(now: Callable[[], float]) -> float:
    return now()
```

The test provides a fixed value for `now`:

```python
# test_clock.py
import clock

def test_stamp() -> None:
    assert clock.stamp(lambda: 100.0) == 100.0
```

`datetime.now()` is harder to patch,
because `datetime` is an immutable C type that rejects attribute assignment,
so the injection approach is worth the small effort.

If you cannot change the code,
the library [`time-machine`](https://github.com/adamchainz/time-machine)
freezes every clock at once, including `datetime.now()`,
with no monkeypatching on your part:

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
but it is the standard answer for code built around `datetime`.

### Network Calls

A test must never use a real network.
The call is slow, it fails whenever the service or the connection does,
and it ties the test to data you do not control.
`monkeypatch` replaces the function that fetches data with one that returns a canned response,
so the test runs offline and gives the same answer every time.
Here a function reads a URL:

```python
# weather.py
from urllib.request import urlopen

def current_temp(city: str) -> str:
    with urlopen(f"https://example.com/{city}") as response:
        return response.read().decode()
```

The test swaps `urlopen()` for a stub that returns bytes from memory,
so no request ever leaves the machine:

```python
# test_weather.py
import io
import pytest
import weather

def test_current_temp(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str) -> io.BytesIO:
        return io.BytesIO(b"21C")
    monkeypatch.setattr(weather, "urlopen", fake_urlopen)
    assert weather.current_temp("denver") == "21C"
```

`weather` imports the function with `from urllib.request import urlopen`,
which copies it into `weather`'s own namespace,
so `weather.urlopen` is the name the call site reads and the name to patch.
Patching `urllib.request.urlopen` instead would leave `weather`'s copy untouched.
The rule covers both cases: patch the name the calling code looks up.
The same approach isolates a database, a message queue, or any other service.
Replace the boundary function with a stand-in and assert against its result.

A stand-in like `fake_urlopen()` is called a *stub*:
it answers with a canned value and records nothing.
The standard library's `unittest.mock` builds stubs for you,
along with *mocks* that also record how they were called,
and you will meet it in most existing code.
This book patches with `monkeypatch` and prefers injection where the code can be changed,
because a function that takes its clock or its fetcher as an argument needs no patching library at all.

## White-Box and Black-Box Tests

A *white-box* test reaches into the internals of the code it checks.
A *black-box* test treats the code as an opaque box and exercises only its public interface,
the way a client would.

A language with access control enforces the two differently.
Python has no access control, so every attribute is reachable.
A single leading underscore, as in `self._balance`,
changes nothing at the language level.
It is stored under that exact name and reachable like any other attribute.
It is only a convention that says, "this is private, do not rely on it."

A leading double underscore does something real,
though it is still not access control.
Python's compiler rewrites `self.__pin`, written inside a class body,
into `self._ClassName__pin`, a transformation called *name mangling*.
`ty` does not model this rewriting,
so its report on the code below disagrees with what actually runs:

```python
# name_mangling.py

class Vault:
    def __init__(self) -> None:
        self._balance = 0  # Single underscore: convention only
        self.__pin = "1234"  # Double underscore: gets mangled

v = Vault()
print(vars(v))
#: {'_balance': 0, '_Vault__pin': '1234'}
# ty: unresolved attribute "_Vault__pin":
print(v._Vault__pin)  # type: ignore
#: 1234
```

`vars(v)` shows what actually got stored: `_balance` under its own name,
and `__pin` rewritten to `_Vault__pin` the moment the class body compiled.
The rewritten name is a real attribute like any other,
so `v._Vault__pin` reads it successfully.
Mangling exists to stop a subclass from accidentally colliding with a base class's private-looking name,
not to hide the attribute.
In Python the distinction between white-box and black-box remains one of discipline,
not of compiler enforcement.

That makes black-box testing the sensible default.
If you test the public surface, the methods a caller is meant to use,
you can change the internals without rewriting the tests.
The `Account` tests are black-box,
which means they never read a private attribute.
When you do need a white-box test for a tricky internal, nothing stops you,
but treat each one as a test that may break when you refactor.

## Property-Based Testing

The tests in this chapter check specific examples:
this input produces that output.
A *property-based* test instead states a law the code must always obey,
and lets a tool generate the inputs that try to break it.
[Assurance](43_Functional_Assurance.md#an-assurance-spectrum)
shows the technique,
including the [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
library that automates it.

## How This Book Runs Its Tests

The build automatically extracts and checks the examples in this book.
It runs plain programs and reports their failures.
It hands files named `test_*.py` and `conftest.py` to `pytest` instead,
and a failing test fails the build.

You can now take an untested function and make it testable.
Name what it depends on: the clock, randomness, the filesystem, the environment,
the network.
Replace those at the boundary,
by injection where you can change the code and with `monkeypatch` where you cannot.
Then pin the behavior that is left with a handful of parametrized cases.
The work is mostly in the first step,
since a function that is hard to test is usually one that goes looking for something it was never handed.

## Exercises

1.  Add a `transfer(other: Account, amount: float)` method to `Account` and write its tests first:
    a successful transfer, and an overdraft that leaves both accounts unchanged.
2.  Use `parametrize` to test `add_interest()` at several rates,
    comparing with `pytest.approx()`.
3.  Write a fixture that `yield`s an `Account` and asserts, after the `yield`,
    that the balance is never negative.
    Use it in two tests.
4.  Write `settings_path()`,
    which returns `Path(os.environ["APP_CONFIG"]) / "settings.ini"`,
    and test it with `monkeypatch` and `tmp_path`.
    Then rewrite the function to take the directory as an argument and test it again.
    Which test would survive a change to the environment variable's name?
