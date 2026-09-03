# Testing

Unit testing is one of the most valuable habits in modern programming.
You build tests into the code you write and run them on every change.
A type checker verifies the claims you can write as annotations.
Tests verify the rest: that a withdrawal reduces the balance,
that the account refuses an overdraft.
They state what the code should do, and check it.

Tests give you a safety net.
With them you can refactor boldly, change designs, and clean up code.
Tests also push back on the design.
A function you cannot test easily is usually one that goes looking for the clock,
the filesystem, or the network instead of receiving them.

Perhaps more importantly,
tests tell you immediately if a change you've made causes a failure.
Immediate feedback saves an enormous amount of time.
If the problem surfaces only after multiple changes,
you have no idea which change caused the bug.

## Test-Driven Development (TDD)

Writing the code, getting it working,
and intending to write the tests later seems easy.
Later rarely comes.
Once the code works, the tests feel less important.

One solution is to write the tests before writing the code.
When you write the tests first, you:

1.  Describe what the code should do, in concrete and verifiable terms,
    not in a separate document that drifts out of date.
2.  Provide a worked example of how to use the code.
3.  Get a clear definition of done: the code is complete when the tests pass.

Testing then becomes a design tool,
not a verification step you skip when the code looks right to you.

That said, TDD requires that you know what you are creating.
It assumes you are confident the design is correct,
so that only implementation remains.
Often, however, you are still experimenting to find the direction the program will take.
When you are discovering the design rather than producing code, TDD is wasteful.

For example, here is a test for `is_palindrome()`,
written before that function exists anywhere in the project:

```python
# test_palindrome.py
from palindrome import is_palindrome

def test_empty_string_is_a_palindrome() -> None:
    assert is_palindrome("")

def test_racecar_is_a_palindrome() -> None:
    assert is_palindrome("racecar")

def test_hello_is_not_a_palindrome() -> None:
    assert not is_palindrome("hello")
```

At this point `palindrome.py` does not exist,
so running this file fails before a single assertion runs:
`pytest` cannot import a module that is not there.
That failure is the point.
It confirms the test would catch a missing implementation, not just a wrong one.
Only now does the implementation appear,
sized to make every case in the test pass and nothing more:

```python
# palindrome.py
def is_palindrome(s: str) -> bool:
    return s == s[::-1]
```

The test written first stayed the same.
Only the code changed to satisfy it.
That is the design-tool benefit TDD promises:
the test already said what "done" means before any implementation existed to argue otherwise.

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

The tests in this chapter check the following `Account` class, a `@dataclass`
([Data Classes as Types](12_Techniques--Data_Classes_as_Types.md) explains the decorator):

```python
# account.py
from dataclasses import dataclass

class InsufficientFunds(Exception):
    def __init__(self,
                 balance: float, amount: float) -> None:
        super().__init__(
            f"balance {balance} is less than {amount}")

@dataclass
class Account:
    balance: float = 0.0

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

This file previews two features that get their own sections later in this chapter:
the `parametrize`[^parametrize] mark runs one test over several inputs,
and the `funded` fixture builds a prepared account for each test that names it as a parameter.
The `@` lines apply decorators, which [Decorators](14_Techniques--Decorators.md)
explains; here they only mark the functions for `pytest`.

Run the test suite by typing `pytest` in the project directory.[^book-tests]
`pytest` puts each test file's own directory at the front of `sys.path`,
so `from account import Account` works with no packaging and no path setup,
as long as `account.py` sits beside `test_account.py`.
`pytest` discovers every `test_*.py` file, collects every `test_` function,
runs them, and reports successes and failures.
A failing `assert` prints the expression and the actual values,
so you rarely need a debugger to see what went wrong.

`pytest -k overdraft` runs only the tests whose names contain "overdraft",
`pytest -x` stops at the first failure,
and `pytest --lf` reruns just the tests that failed last time.
Those three cover most of a working day.

If you change the expected value in `test_deposit_increases_balance()` to `10`,
the report names the line, the expression, and both sides:

```text
______________ test_deposit_increases_balance ______________

    def test_deposit_increases_balance() -> None:
        account = Account()
        account.deposit(100)
>       assert account.balance == 10
E       assert 100.0 == 10
E        +  where 100.0 = Account(balance=100.0).balance

test_account.py:11: AssertionError
```

The `where` line is the rewriting at work:
`pytest` keeps the sub-expression `account.balance` and its value,
which a bare `assert` statement would discard.
`Account` is a `@dataclass`,
so its generated `__repr__()` names the field values.
A hand-written class with no `__repr__()` would print `<account.Account object>` there instead.

## Testing for Exceptions

`test_overdraft_raises()` uses `pytest.raises()` as a context manager.
The test passes only if the block raises the expected exception.

Keep the `with` block down to the single call that should fail.
Any statement inside it that raises the expected type passes the test,
including one that fails for an unrelated reason.
`match=` takes a regular expression that `pytest` checks against the exception's message,
so the test can confirm which failure occurred and not just its type:

```python
# test_overdraft_message.py
import pytest
from account import Account, InsufficientFunds

def test_overdraft_reports_the_shortfall() -> None:
    account = Account(100)
    with pytest.raises(InsufficientFunds,
                       match="less than 250"):
        account.withdraw(250)
    assert account.balance == 100
```

The assertion after the block belongs outside it:
a failed withdrawal must leave the balance alone,
and that check has nothing to do with the exception.
Inside the block it would never run:
the exception from `withdraw()` skips the rest of the block,
and `pytest.raises()` then absorbs it.

## Comparing Floating-Point Values

Testing floating-point results for exact equality is unreliable.
`test_interest_uses_approx()` compares with `pytest.approx()`,
which allows a small tolerance: a relative difference of 1e-6,
unless you pass `rel=` or `abs=`.

That test would pass with `==` as well.
`100.0 + 100.0 * 0.05` is exactly `105.0` on any IEEE double,
and so is every other whole-percent rate on this starting balance.
The trouble starts once error accumulates:

```python
# test_compounding.py
import pytest
from account import Account

def test_interest_compounds() -> None:
    account = Account(100)
    for _ in range(5):
        account.add_interest(0.05)
    assert account.balance == pytest.approx(127.62815625)
```

Applying 5% five times produces `127.62815624999999`,
so the same assertion written with `==` against `127.62815625` fails.
Use `approx()` as the habit rather than as the rescue:
the first test does not need it,
and you cannot tell by looking which of the two you are writing.

## Parametrizing Tests

When the same logic should run against several inputs, do not copy the test.
Mark the test with `parametrize`, as `test_nonpositive_deposit_raises()` does,
and `pytest` runs it once per case and reports each separately.
That single function becomes three independent tests,
and a failure names the case that failed.

A `parametrize` mark can carry several names, followed by a list of tuples,
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
so `pytest` builds three independent tests.
The names in the string line up, in order, with the values in each tuple.

`parametrize` is a *mark*, and three others turn up in any existing suite.
`@pytest.mark.skip` and `@pytest.mark.skipif` leave a test out,
unconditionally or on a condition such as the platform.
`@pytest.mark.xfail` records a known bug: the test still runs,
`pytest` reports a failure as expected rather than as a break,
and the suite stays green without anyone deleting the test that proves the bug.

## Fixtures Replace Setup and Teardown

JUnit-style frameworks give each test class a `setUp()` and `tearDown()`.
`pytest` replaces both with *fixtures*: functions that build what a test needs.
You declare fixtures as parameters to a test,
and each parameter name tells `pytest` to call that fixture and pass its result to the test.

The `funded` function in `test_account.py` is a fixture.
`pytest` is the only thing that calls it:
a test that calls `funded()` fails with `Fixture "funded" called directly`.

Each test gets its own freshly built `funded` account,
so tests cannot leak state into each other.
If a fixture needs cleanup,
it can `yield` the value and run teardown code after the `yield`.
A function containing `yield` is a generator.
[Iterators](23_Patterns--Iterators.md#generators) covers the mechanism,
and this chapter needs only the shape.
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
Everything after it runs once the test finishes, even if the test fails.
Close files, release locks, or check a final invariant after the `yield`.
A failing check there surfaces as an error, not as a test failure:
`pytest` prints `1 passed, 1 error`,
so read the error to see which invariant broke.

A fixture marked `@pytest.fixture(autouse=True)` runs for every test in its scope without any test naming it.
That suits a fixture whose value is a side effect rather than an object:
resetting a global registry, or installing a `monkeypatch` every test needs.
Autouse runs the fixture, and only a parameter delivers its value.
Mark `funded` autouse, leave it out of the parameter list,
and `funded.withdraw(40)` raises an `AttributeError`:
the bare name finds the fixture function, not the `Account` it returns.

Fixtures eliminate duplicated setup.
A test that names `funded` states what it needs and nothing about how to build it.

## Sharing Fixtures with conftest.py

Any test in `conftest.py`'s directory, or below it,
can use a fixture defined there, with no import.
Place shared setup in `conftest.py`.

A directory has one `conftest.py`, so its fixtures accumulate in that file.
This one holds two, and they demonstrate different things:

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

Take `bank_name` first.
`pytest` builds the `scope="session"` fixture once and reuses it,
and that reuse suits expensive resources.
The reuse is the risk as well as the point: every test receives the same object,
so one test that mutates it changes what the next test sees.
A session fixture that returns a mutable object shows the leak directly:

```python
# test_session_leak.py
import pytest

@pytest.fixture(scope="session")
def shared_cache() -> dict[str, int]:
    return {}

def test_first_write(
    shared_cache: dict[str, int]
) -> None:
    shared_cache["seen"] = 1
    assert shared_cache == {"seen": 1}

def test_second_sees_leftover(
    shared_cache: dict[str, int]
) -> None:
    # The dict test_first_write() left behind,
    # not a fresh one.
    assert shared_cache == {"seen": 1}
```

Both tests pass, and that is the problem:
`test_second_sees_leftover()` only passes because `test_first_write()` ran first and left its entry behind.
Swap the two functions' order in the file and `test_second_sees_leftover()` fails,
since nothing has written `"seen"` yet.
Keep session fixtures to values nothing modifies, like `bank_name`,
or to a resource with its own reset,
and leave anything a test mutates at the default per-test scope.

`preloaded` shows the other feature: you can parametrize a fixture.
Every test that requests it runs once for each parameter value,
with `request.param` holding the value for that run.
`pytest` rebuilds `preloaded` for each parameter,
so a test that uses it automatically runs at every starting balance:

```python
# test_fixtures.py
from account import Account

def test_deposit_on_any_balance(preloaded: Account) -> None:
    start = preloaded.balance
    preloaded.deposit(1)
    assert preloaded.balance == start + 1

def test_bank_name_from_conftest(bank_name: str) -> None:
    assert bank_name == "Crunchy Frog Credit Union"
```

Nothing imports either fixture.
`pytest` finds them in `conftest.py` and supplies them by name.

`parametrize` multiplies the one test it decorates.
A parametrized fixture multiplies every test that requests it,
in this file and every other file that can see the `conftest.py`.
Use the mark when the cases belong to one test,
and the fixture when the same variation should sweep across a whole suite.

## White-Box and Black-Box Tests

A *white-box* test reaches into the internals of the code it checks.
A *black-box* test treats the code as an opaque box and exercises only its public interface,
the way a client would.

In a language with access control, the compiler enforces the difference.
Python has no access control, so every attribute is reachable.
A single leading underscore, as in `self._balance`,
changes nothing at the language level.
Python stores it under that exact name, reachable like any other attribute.
Only convention says, "this is private, do not rely on it."

A leading double underscore changes the name Python stores,
though it is still not access control.
Python's compiler rewrites `self.__pin`, written inside a class body,
into `self._ClassName__pin`, a transformation called *name mangling*.
`ty` does not model this rewriting,
so its report on the code below disagrees with what actually runs:

```python
# name_mangling.py

class Vault:
    def __init__(self) -> None:
        # Single underscore: convention only
        self._balance = 0
        # Double underscore: gets mangled
        self.__pin = "1234"

v = Vault()
print(vars(v))
#: {'_balance': 0, '_Vault__pin': '1234'}
# ty: unresolved attribute "_Vault__pin":
print(v._Vault__pin)  # type: ignore
#: 1234
```

`vars(v)` shows what Python actually stored: `_balance` under its own name,
and `__pin` rewritten to `_Vault__pin` the moment the class body compiled.
The rewritten name is a real attribute like any other,
so `v._Vault__pin` reads it successfully.
Mangling exists to stop a subclass from accidentally colliding with a base class's private-looking name,
not to hide the attribute.
In Python the distinction between white-box and black-box remains one of discipline,
not of compiler enforcement.

That makes black-box testing the sensible default.
If you test the public surface, the methods a caller should use,
you can change the internals without rewriting the tests.
The `Account` tests are black-box: they read no private attributes.
When you do need a white-box test for a tricky internal, nothing stops you,
but treat each one as a test that may break when you refactor.

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

`data_dir()` reads `APP_DATA` on every call,
so `monkeypatch.setenv()` can redirect it.
A module-level `DATA_DIR = Path(os.environ.get("APP_DATA", "."))` would read the variable once,
at import time, before any test body runs,
so patching the environment afterward would change nothing.
Reading a setting where you use it, rather than caching it at import,
is most of what makes a module testable.

### Random Numbers

Code that calls `random` produces a different value each run,
so a test cannot assert a fixed result:

```python
# dice.py
import random

def roll() -> int:
    return random.randint(1, 6)
```

`monkeypatch` replaces the random call with one that returns a known value,
so the result stays predictable while the test runs:

```python
# test_dice.py
import dice
import pytest

def test_roll_returns_known_value(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(dice.random, "randint",
                        lambda a, b: 4)
    assert dice.roll() == 4
```

`import random` binds the one module object every importer shares,
so `dice.random` and `random` are the same object and the patch replaces `randint()` process-wide.
`monkeypatch` restores the original when the test ends,
and that restoration is what makes a process-wide patch safe.

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
The `4` here is what `Random(0)` produces first,
and its match with the stubbed value in `test_dice.py` is a coincidence:
as with any seed, you record the value it gives you rather than pick one.

Injection is not free.
The `rng` or `now` parameter must appear on every function between the caller and the code that needs it,
which several calls deep in a real codebase means widening a signature all the way up the call stack,
or introducing a context object to carry it.
`monkeypatch` skips that plumbing: it patches the name in place,
at the cost of the global, restore-on-teardown patch shown above.
Choose injection when the parameter already sits near the boundary.
Choose `monkeypatch` when threading it through would touch more code than the test is worth.

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
The same computation takes `now` as an argument instead of going looking for it:

```python
# clock_injected.py
from collections.abc import Callable

def elapsed(start: float,
            now: Callable[[], float]) -> float:
    return now() - start
```

The test hands it a fixed value:

```python
# test_clock_injected.py
import clock_injected

def test_elapsed() -> None:
    assert clock_injected.elapsed(
        40.0, lambda: 100.0) == 60.0
```

Both tests check the same arithmetic.
The injected one runs with no `monkeypatch`,
and its signature says where the time comes from.

`datetime.now()` is harder to patch,
because `datetime` is an immutable C type that rejects attribute assignment,
so the injection approach is worth the small effort.

If you cannot change the code,
the library [`time-machine`](https://github.com/adamchainz/time-machine)
freezes every source of wall-clock time at once, including `datetime.now()`,
with no monkeypatching on your part:

```python
# event.py
from datetime import datetime

def current_year() -> int:
    return datetime.now().year
```

```python
# test_event.py
from datetime import datetime
import event
import time_machine

@time_machine.travel("2030-06-15", tick=False)
def test_current_year_is_frozen() -> None:
    assert event.current_year() == 2030
    # tick=False: successive readings are identical
    assert datetime.now() == datetime.now()
```

`travel` sets the clock to the given moment for the test,
and `tick=False` holds it there so every reading is identical,
as the test's second assertion shows.
`time.monotonic()` and `time.perf_counter()` keep running,
because they measure elapsed intervals rather than dates.
Unlike `monkeypatch`, `time-machine` is a third-party dependency,
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
so no request leaves the machine:

```python
# test_weather.py
import io
import pytest
import weather

def test_current_temp(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_urlopen(url: str) -> io.BytesIO:
        return io.BytesIO(b"21C")
    monkeypatch.setattr(weather, "urlopen", fake_urlopen)
    assert weather.current_temp("denver") == "21C"
```

`weather` imports the function with `from urllib.request import urlopen`,
and that statement binds `urlopen` in `weather`'s own namespace,
so `weather.urlopen` is the name the call site reads and the name to patch.
Patching `urllib.request.urlopen` instead would leave `weather`'s copy untouched.
The rule covers both cases: patch the name the calling code looks up.
The same approach isolates a database, a message queue, or any other service.
Replace the boundary function with a stand-in and assert against its result.

A stand-in like `fake_urlopen()` is a *stub*:
it answers with a canned value and records nothing.
The standard library's `unittest.mock` builds stubs for you,
along with *mocks* that also record the calls they receive,
and it turns up in most existing code.
A `Mock` goes further than a stub: it remembers every call it received,
so a test can check the call itself, not just what it returned.

```python
# notifier.py
from collections.abc import Callable

def notify_low_balance(
    balance: float,
    send: Callable[[str], None],
) -> None:
    if balance < 0:
        send(f"balance is negative: {balance}")
```

```python
# test_notifier.py
from unittest.mock import Mock
import notifier

def test_negative_balance_sends_message() -> None:
    send = Mock()
    notifier.notify_low_balance(-5, send)
    send.assert_called_once_with(
        "balance is negative: -5")
```

`Mock()` accepts any call and returns another `Mock` unless told otherwise,
recording every call as it goes.
`assert_called_once_with()` checks two things at once:
that `send` ran exactly once, and that it ran with this exact argument.
A plain stub cannot make that check.
`fake_urlopen()` has no memory of how it was called.
This book patches with `monkeypatch` and prefers injection where you can change the code,
because a function that takes its clock or its fetcher as an argument needs no patching library.

## Property-Based Testing

The tests in this chapter check specific examples:
this input produces that output.
A *property-based* test instead states a law the code must always obey,
and lets a tool generate the inputs that try to break it.
[Confidence](43_Functional--Confidence.md#a-confidence-spectrum)
shows the technique,
including the [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
library that automates it.

## Making Code Testable

You can now take an untested function and make it testable.
Name what it depends on: the clock, randomness, the filesystem, the environment,
the network.
Replace those at the boundary,
by injection where you can change the code and with `monkeypatch` where you cannot.
Then pin the remaining behavior with a handful of parametrized cases.
The work is mostly in the first step,
since a function that is hard to test is usually one that goes looking for something no caller handed it.

To find out what you have not tested, run the suite under `coverage.py`,
which the `pytest-cov` plugin wires up when you pass `--cov`.
Read the result as a list of lines nothing exercised, not as a score:
a line a test happened to execute is not the same as a line a test checks.

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
5.  `weather.current_temp()` calls `urlopen()`.
    Write a second function that takes a fetcher as an argument instead,
    and test both: one with `monkeypatch`, one with a plain function passed in.
    Then rename `weather.urlopen` to `weather.fetch` and see which test still passes.

[^parametrize]: Four spellings are in use, all correct.
    The stem is `parametr-` or `parameter-`.
    The suffix is `-ize` in the US
    or `-ise` in the UK and Commonwealth countries.
    The two choices are independent,
    giving `parametrize`, `parametrise`, `parameterize`, and `parameterise`.
    This book follows pytest's own spelling for `@pytest.mark.parametrize`,
    and uses "parameterize" everywhere else,
    for the general sense of a class or function taking a parameter.

[^book-tests]: This book's own build extracts every listing,
    including this chapter's `test_*.py` and `conftest.py` files,
    and hands them to `pytest` instead of running them as plain programs.
    A failing test fails the build,
    the same way a failing type check or an unexpected exception does
    elsewhere in the book.
