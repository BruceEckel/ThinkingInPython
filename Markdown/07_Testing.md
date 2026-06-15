# Testing

> Testing is flawed, but not testing is reckless.

One of the most valuable habits in modern programming is unit testing. You
build tests into the code you write and run them on every change. It is as if
you extend the language: the test suite checks not just that the code parses,
but that it still means what you intended.

Unit testing is not a design pattern but a development
practice. Its effect on the quality of this book is large enough that tests
appear throughout, so the practice is introduced here.

Tests give you a safety net. With them you can refactor boldly, change designs,
and clean up code, because a regression announces itself immediately instead of
months later in a bug report. The cost is small and the payoff compounds.

## Write Tests First

A common failure is to write the code, get it working, and intend to write the
tests later. Later rarely comes. The tests lose importance and then vanish.

The fix, drawn from Extreme Programming, is to write the tests *before* the
code. This seems backwards, but it gives testing enough value to make it
essential. When you write the tests first, you:

1.  Describe what the code should do, in concrete and verifiable terms, not in
    a separate document that drifts out of date.
2.  Provide a worked example of how the code is meant to be used.
3.  Get a clear definition of done: the code is finished when the tests pass.

Testing then becomes a design tool, not a verification step you skip when you
happen to feel good about the code you just wrote. That feeling is usually
wrong.

## pytest

Python has a testing framework in the standard library, `unittest`, modeled on
Java's JUnit. It works, but it carries the class-based boilerplate of its
heritage. The wider Python world has settled on `pytest`, and so does this
book.

`pytest` is built around two ideas that keep tests short. A test is just a
function whose name starts with `test_`. A check is just the `assert`
statement. There is no base class to inherit and no special assertion methods
to memorize. `pytest` rewrites `assert` so that a failure still shows you both
sides of the comparison.

Here is a small unit to test. Put it in its own file:

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

By convention tests live in a file whose name starts with
`test_`. The following file exercises the whole `Account` class, and the sections
below walk through each technique it uses:

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

Run the test suite by typing `pytest` in the project. It discovers every
`test_*.py` file, collects every `test_` function, runs them, and reports. A
passing run is quiet. A failing `assert` prints the expression and the actual
values, so you rarely need a debugger to see what went wrong.

## Fixtures Replace setup and teardown

JUnit-style frameworks give each test class a `setUp()` and `tearDown()`.
`pytest` replaces both with *fixtures*: functions that build what a test needs,
declared as parameters. The `funded` function above is a fixture. A test that
names `funded` as an argument receives the value the fixture returns.

```python
@pytest.fixture
def funded() -> Account:
    account = Account()
    account.deposit(100)
    return account
```

Each test gets its own freshly built `funded` account, so tests cannot leak
state into each other. If a fixture needs cleanup, it can `yield` the value and
run teardown code after the `yield`.

## Testing for Exceptions and Floating Point

Two checks come up constantly. The first is "this call should raise."
`test_overdraft_raises` uses `pytest.raises` as a context manager; the test
passes only if the expected exception is raised inside the block. The second is
comparing floating-point numbers, where exact equality is a trap.
`test_interest_uses_approx` compares with `pytest.approx`, which allows a small
tolerance. Both techniques appear in `test_account.py` above.

## Parametrizing Tests

When the same logic should run against several inputs, do not copy the test.
Mark it with `parametrize`, as `test_nonpositive_deposit_raises` does, and
`pytest` runs it once per case, reporting each separately. That single function
becomes three independent tests, and a failure names the exact case that broke.

## Sharing Fixtures with conftest.py

A fixture defined in a file named `conftest.py` is available to every test in
that directory and below, with no import. This is where shared setup lives.

Fixtures can also be *parametrized*, which multiplies coverage for free: every
test that requests the fixture runs once for each parameter value.

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

The `scope="session"` fixture is built once and reused, which is useful for
expensive resources. The `preloaded` fixture is rebuilt for each parameter, so
a test that uses it is automatically checked at every starting balance:

```python
# test_fixtures.py
from account import Account


def test_deposit_on_any_balance(
    preloaded: Account, bank_name: str
) -> None:
    start = preloaded.balance
    preloaded.deposit(1)
    assert preloaded.balance == start + 1
    assert bank_name  # the session fixture is available everywhere
```

Neither fixture is imported. `pytest` finds them in `conftest.py` and supplies
them by name.

## Isolating Tests from the World

Good tests do not depend on the real filesystem, clock, network, or
environment. `pytest` ships built-in fixtures for this. `tmp_path` gives each
test a private temporary directory. `monkeypatch` sets and restores environment
variables and attributes, undoing every change when the test ends.

Here is a unit that reads an environment variable and touches files:

```python
# storage.py
# A unit that depends on the filesystem and the environment.
import os
from pathlib import Path


def data_dir() -> Path:
    return Path(os.environ.get("APP_DATA", "."))


def save(name: str, value: str) -> None:
    (data_dir() / name).write_text(value, encoding="utf-8")


def load(name: str) -> str:
    return (data_dir() / name).read_text(encoding="utf-8")
```

The tests redirect it at a throwaway directory, so they never touch real data
and never collide with each other:

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

A *white-box* test reaches into the internals of the code it checks. A
*black-box* test treats the code as an opaque box and exercises only its public
interface, the way a client would.

In a language with access control, the two are enforced differently. Python has
no access control. Every attribute is reachable, and a leading underscore is
only a convention that says "this is private, do not rely on it." So in Python
the distinction is one of discipline, not of compiler enforcement.

That makes black-box testing the sensible default. Test the public surface, the
methods a caller is meant to use, and you stay free to change the internals
without rewriting the tests. The `Account` tests are black-box: they never read
a private attribute. When you do need a white-box test for a tricky internal,
nothing stops you, but treat each one as a test that may break when you
refactor.

## How This Book Runs Its Tests

The examples in this book are extracted from the chapters and checked
automatically. Plain programs are run, and their failures are reported. Files
named `test_*.py` and `conftest.py` are handed to `pytest` instead, and a
failing test fails the build. The tests in this chapter run exactly that way.

## Exercises

1.  Add a `transfer(other, amount)` method to `Account` and write its tests
    first: a successful transfer, and an overdraft that leaves both accounts
    unchanged.
2.  Use `parametrize` to test `add_interest` at several rates, comparing with
    `pytest.approx`.
3.  Write a fixture that `yield`s an `Account` and asserts, after the `yield`,
    that the balance is never negative. Use it in two tests.
