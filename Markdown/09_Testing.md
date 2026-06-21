# Testing

> Testing is flawed, but not testing is reckless.

One of the most valuable habits in modern programming is unit testing.
You build tests into the code you write and run them on every change.
It is as if you extend the language:
the test suite checks not just that the code parses,
but that it still means what you intended.

Unit testing is a development practice.
Tests give you a safety net.
With them you can refactor boldly, change designs, and clean up code.
A failing test announces itself immediately instead of months later in a bug report.
The cost is small and the payoff compounds.

## Test-Driven Development (TDD)

A common approach is to write the code, get it working,
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
The design is there, you are confident it is correct, and it is now a matter of implementation.
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

Here is a small unit to test:

```python
# account.py
# The unit under test.


class InsufficientFunds(Exception):
    pass


class Account:
    def __init__(self, balance: float = 0.0) -> None:
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise InsufficientFunds(
                f"balance {self.balance} is less than {amount}")
        self.balance -= amount

    def add_interest(self, rate: float) -> None:
        self.balance += self.balance * rate
```

By convention tests live in a file whose name starts with `test_`.
The following file exercises the whole `Account` class:

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


@pytest.mark.parametrize("bad", [0, -1, -100])
def test_nonpositive_deposit_raises(bad: float) -> None:
    with pytest.raises(ValueError):
        Account().deposit(bad)
```

Run the test suite by typing `pytest` in the project.
It discovers every `test_*.py` file, collects every `test_` function, runs them,
and reports.
A passing run is quiet.
A failing `assert` prints the expression and the actual values,
so you rarely need a debugger to see what went wrong.

## Testing for Exceptions and Floating Point

There are two common special needs in testing, both of which appear in `test_account.py`.

The first is "this call should raise."
`test_overdraft_raises` uses `pytest.raises` as a context manager;
the test passes only if the expected exception is raised inside the block.

The second is comparing floating-point numbers, where exact equality is a trap.
`test_interest_uses_approx` compares with `pytest.approx`,
which allows a small tolerance.

## Parametrizing Tests

When the same logic should run against several inputs, do not copy the test.
Mark it with `parametrize`, as `test_nonpositive_deposit_raises` does,
and `pytest` runs it once per case, reporting each separately.
That single function becomes three independent tests,
and a failure names the exact case that broke.

## Fixtures Replace Setup and Teardown

JUnit-style frameworks give each test class a `setUp()` and `tearDown()`.
`pytest` replaces both with *fixtures*: functions that build what a test needs.
These fixtures are declared as parameters to the test functions,
which tells `pytest` to automatically call the fixture function and pass its result to the test function.

The `funded` function above is a fixture.
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

## Sharing Fixtures with conftest.py

A fixture defined in a file named `conftest.py` is available to every test in that directory and below,
with no import.
This is where shared setup lives.

Fixtures can also be *parametrized*, which multiplies coverage for free:
every test that requests the fixture runs once for each parameter value.

```python
# conftest.py
import pytest
from account import Account


@pytest.fixture(scope="session")
def bank_name() -> str:
    "Built once for the whole test session."
    return "BeanMeUp Savings"


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

Here is a unit that depends on the filesystem and the environment:
it reads an environment variable and touches files:

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
