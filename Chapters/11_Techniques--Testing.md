# Testing

> Every change can break code you are not looking at.
> A test states what the code should do and reports the moment that stops being true.

Unit testing is one of the most valuable habits in modern programming.
You build tests into the code you write and run them on every change.
A type checker verifies the claims you can write as annotations.
Tests verify the rest: that a withdrawal reduces the balance,
that the account refuses an overdraft.

Tests report the behavior a change breaks.
With them you can refactor boldly, change designs, and clean up code.

Tests report a failure immediately, as soon as a change you've made causes it.
Immediate feedback saves an enormous amount of time.
If you discover the problem after multiple changes,
any one of them could have caused the bug.

Tests also expose problems in the design.
A function that is hard to test usually reads the clock, the filesystem,
or the network instead of receiving them as arguments.

When you find a bug that no test caught, the patch is half the job.
Start by writing a test that reproduces the bug, and watch it fail.
The fix then turns that test green.
If the bug returns, that test reports it.
The other half of the job is asking what allowed the bug:
a case the tests missed, a claim the annotations left out,
an interface that makes misuse easy.
Fix the bug, and also fix its cause.
A team that stops at the patch fixes the same kind of bug forever.

## Test-Driven Development (TDD)

Writing the code, getting it working,
and intending to write the tests later seems easy.
Later rarely comes.
Once the code works, the tests feel less important.

One solution is to write the tests before writing the code.
When you write the tests first, you:

1.  Describe what the code should do, in concrete and verifiable terms,
    not in a separate document that stops matching the code.
2.  Provide a worked example of how to use the code.
3.  Get a clear definition of done: the code is complete when the tests pass.

Testing then becomes a design tool,
not a verification step you skip when the code looks right to you.

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
so running this file fails before a single assertion runs.
The import at the top of the file raises a `ModuleNotFoundError`,
which `pytest` reports as a collection error.
That error, rather than a failing assertion,
confirms the test detects a missing implementation.

```python
# palindrome.py
def is_palindrome(s: str) -> bool:
    return s == s[::-1]
```

The test written first stays the same.
Only the code changes to satisfy it.
The test defines what "done" means before any implementation exists to shape that definition.

But TDD requires that you know what you are creating.
It assumes you are confident the design is correct,
so that only implementation remains.
Often, however, you are still experimenting to find out what the program should do.
When you are discovering the design rather than producing code, TDD is wasteful.

## pytest

Python has a testing framework in the standard library, `unittest`,
modeled on Java's JUnit.
`unittest` works, but it requires the class-based boilerplate of the JUnit design.
Most Python projects use `pytest`, and so does this book.

`pytest` uses two ideas that keep tests short.
A test is a function whose name starts with `test_`.
A check is Python's built-in `assert` statement.
No base class needs inheriting,
and no special assertion methods need memorizing.
`pytest` rewrites `assert` so that a failure shows you both sides of the comparison.

Most of this chapter's tests check the following `Account` class,
a [`@dataclass`](12_Techniques--Data_Classes_as_Types.md#data-classes):

```python
# account.py
from dataclasses import dataclass

class InsufficientFunds(Exception):
    def __init__(self,
                 balance: float, amount: float) -> None:
        super().__init__(
            f"balance {balance} is less than {amount}")
        self.balance = balance
        self.amount = amount

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

By convention, tests live in a file whose name starts with `test_`.

The test file confirms that:

- A new account starts empty.
- A deposit increases the balance.
- A deposit of zero or less raises a `ValueError`.
- A withdrawal reduces the balance.
- An overdraft raises `InsufficientFunds`.
- Interest adds to the balance.

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

def test_interest_adds_to_balance(funded: Account) -> None:
    funded.add_interest(0.05)
    assert funded.balance == pytest.approx(105.0)
```

This file previews two features that get their own sections later in this chapter.
The `parametrize`[^parametrize] mark runs one test over several inputs.
`test_nonpositive_deposit_raises()` becomes three tests, with `bad` set to `0`,
`-1`, and `-100` in turn.
The `funded` fixture builds a prepared account for each test that names it as a parameter.
The `@` lines apply [decorators](14_Techniques--Decorators.md).
Here they mark the functions for `pytest`.

Run the test suite by typing `pytest` in the project directory.[^book-tests]
`pytest` puts each test file's own directory at the front of [`sys.path`](06_Foundations--Modules_and_Packages.md#pythonpath),
so `from account import Account` works with no packaging and no path setup,
as long as `account.py` sits beside `test_account.py`.
`pytest` discovers every `test_*.py` file, collects every `test_` function,
runs them, and reports successes and failures.
A failing `assert` prints the expression and the actual values,
so you rarely need a debugger to see what went wrong.

When you do need one, a `breakpoint()` call,
in the test or in the code it checks, pauses the run at that line in `pdb`.
`breakpoint()` calls `sys.breakpointhook()`,
which reads the `PYTHONBREAKPOINT` environment variable,
so that variable can turn every `breakpoint()` off with `0` or specify another debugger in place of `pdb`.

`pytest -k overdraft` runs only the tests whose names contain "overdraft",
`pytest -x` stops at the first failure,
and `pytest --lf` reruns the tests that failed last time.
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

The `where` line comes from the assertion rewriting.
`pytest` keeps the sub-expression `account.balance` and its value,
which a bare `assert` statement discards.

Because `Account` is a `@dataclass`,
its generated `__repr__()` prints `Account(balance=100.0)`.
A hand-written class with no `__repr__()` prints `<account.Account object at 0x...>` there.

## Testing for Exceptions

`test_overdraft_raises()` uses `pytest.raises()` as a [context manager](15_Techniques--Context_Managers.md).
The test passes only if the block raises the expected exception.

Keep the `with` block down to the single call that should fail.
Any statement inside it that raises the expected type passes the test,
including one that fails for an unrelated reason.

`match=` takes a regular expression that `pytest` checks against the exception's message,
so the test can confirm which failure occurred as well as its type:

```python
# test_overdraft_message.py
import pytest
from account import Account, InsufficientFunds

def test_overdraft_names_amount_keeps_balance() -> None:
    account = Account(100)
    with pytest.raises(InsufficientFunds,
                       match="less than 250") as excinfo:
        account.withdraw(250)
    assert excinfo.value.amount == 250
    assert account.balance == 100
```

`pytest` applies the pattern with `re.search()`,
so the pattern can match any part of the message.
The full message here is `balance 100 is less than 250`.
`re.prefixmatch()`, new in Python 3.15,
anchors a pattern at the start of the string,
so it rejects `less than 250` for this message, which starts with `balance`.
Its old name, `re.match()`, is now soft-deprecated,
since that name hides the anchoring and reads like the `match` statement.
If the message holds `.`, `(`, or another regular-expression metacharacter,
pass the copied text through `re.escape()` so the pattern matches it literally.

`as excinfo` binds an `ExceptionInfo` object, and once the block exits,
`excinfo.value` holds the exception that `withdraw()` raised.
`InsufficientFunds` stores `balance` and `amount` as attributes,
so the test checks `excinfo.value.amount` as a number.
A reworded message breaks the `match=` pattern when the test runs,
while the type checker reports a renamed attribute before the run.

Both assertions belong after the block, not inside it.
The exception from `withdraw()` skips the rest of the block,
and `pytest.raises()` then catches and suppresses it,
so neither assertion would run inside the block.
The balance assertion checks a separate claim:
a failed withdrawal must leave the balance alone.

## Comparing Floating-Point Values

Testing floating-point results for exact equality is unreliable.
`test_interest_adds_to_balance()` compares with `pytest.approx()`,
which allows a small tolerance: a relative difference of 1e-6 by default,
adjustable through `rel=` or `abs=`.
Outside a test, use the standard-library counterpart, `math.isclose()`.
Its default relative tolerance is a tighter 1e-9,
adjustable through its `rel_tol` and `abs_tol` arguments.

That test passes with `==` as well.
`100.0 + 100.0 * 0.05` is exactly `105.0` on any IEEE double,
and every other whole-percent rate on this starting balance gives an exact result too.
The exact comparison fails when rounding error accumulates:

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
Use `approx()` for every floating-point comparison from the start.
Some tests pass with `==`, as `test_interest_adds_to_balance()` does.
You cannot tell by looking which ones need `approx()`.

## Parametrizing Tests

When the same logic should run against several inputs,
write one test and mark it with `parametrize`,
as `test_nonpositive_deposit_raises()` does.
`pytest` runs the test once per case and reports each separately.
That single function becomes three independent tests.
A failure names the case that failed.

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

The names in the string line up, in order, with the values in each tuple.

`parametrize` is a *mark*, and three others appear in most existing suites.
`@pytest.mark.skip` and `@pytest.mark.skipif` leave a test out,
unconditionally or on a condition such as the platform.
`@pytest.mark.xfail` records a known bug.
The test still runs.
`pytest` counts the test's failure as expected rather than as a new break.
The suite stays green, and the test that proves the bug stays in place.

## Fixtures Replace Setup and Teardown

JUnit-style frameworks give each test class a `setUp()` and `tearDown()`.
`pytest` replaces both with *fixtures*: functions that build what a test needs.
You declare fixtures as parameters to a test.
Each parameter name tells `pytest` to call that fixture and pass its result to the test.

The `funded()` function in `test_account.py` is a fixture.
Only `pytest` calls it.
A test that calls `funded()` fails with `Fixture "funded" called directly`.

Each test gets its own freshly built `funded` account,
so every test starts from a balance of 100,
whatever earlier tests did to their accounts.

If a fixture needs cleanup,
it can `yield` the value and run teardown code after the `yield`.
A function containing `yield` is a [generator](22_Patterns--Iterators.md#generators),
a construct a later chapter covers.
A fixture uses one part of generators, the `yield` statement,
which divides the fixture into the code before it and the code after it:

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
Everything after it runs once the test finishes,
whether the test passes or fails.
Close files, release locks, or check a final invariant after the `yield`.
Do the cleanup first,
because a failing check raises an `AssertionError` that skips the rest of the teardown.

`pytest` reports a failing check after the `yield` as an error,
not as a test failure.
It prints `1 passed, 1 error`, so read the error to see which invariant broke.

A fixture marked `@pytest.fixture(autouse=True)` runs for every test in its scope without any test naming it.
Autouse suits a fixture whose value is a side effect rather than an object:
resetting a global registry, or installing a `monkeypatch` every test needs,
as `test_storage.py` does later in this chapter.

Autouse runs the fixture.
Only a parameter delivers the fixture's value.
If you mark `funded` autouse and leave it out of the parameter list,
the bare name `funded` refers to the fixture object the decorator returns,
rather than the `Account` the function returns.
`funded.withdraw(40)` then raises an `AttributeError`.

Fixtures eliminate duplicated setup.
A test that names `funded` states what it needs and leaves the building to the fixture.

## Sharing Fixtures with conftest.py

When several test files need the same fixture,
put it in a file named `conftest.py`.
`pytest` loads that file on its own.
Any test in `conftest.py`'s directory, or below it,
can use a fixture defined there, with no import.

A directory has at most one `conftest.py`,
so all of that directory's shared fixtures go in the one file.
Here that file holds a session-scoped fixture and a parametrized one:

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

`pytest` builds the session-scoped `bank_name` fixture once and reuses it,
which suits resources that are slow to build.
The reuse saves that build time, and it is also the risk.
Because every test receives the same object,
one test that mutates it changes what the next test sees.
A session fixture that returns a mutable object shows the leak:

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
    assert shared_cache == {"seen": 1}
```

Both tests pass, and that is the problem.
`test_second_sees_leftover()` passes for one reason:
`test_first_write()` ran first and left its entry behind.
If you swap the two functions' order in the file,
`test_second_sees_leftover()` fails, since `shared_cache` is still empty.
Keep session fixtures to immutable values, like `bank_name`,
or to a resource with its own reset,
and leave anything a test mutates at the default per-test scope.

`preloaded`, the other fixture in `conftest.py`,
shows that you can parametrize a fixture.
`preloaded` receives `request`, a built-in fixture, by naming it as a parameter.
`request.param` holds one value from `params` for each build.
`pytest` builds `preloaded` once for each parameter value,
so every test that requests it runs once per value,
here at every starting balance:

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

`parametrize` multiplies the one test it marks.
A parametrized fixture multiplies every test that requests it,
in `test_fixtures.py` and every other file that can see the `conftest.py`.
Use the mark when the cases belong to one test,
and the fixture when every test in a suite should run over the same values.

## White-Box and Black-Box Tests

A *white-box* test reads the internals of the code it checks.
A *black-box* test treats the code as an opaque box and exercises only its public interface,
the way a client does.

In a language with access control, the compiler enforces the difference.
Python has no access control, so every attribute is reachable.
To the language, the single leading underscore in `self._balance` is one more character in the attribute's name.
Python stores `_balance` under that name, reachable like any other attribute.
Only convention says, "this is private, do not rely on it."

A leading double underscore changes the name Python stores,
though it is still not access control.
Inside a class body,
Python's compiler rewrites `self.__pin` into `self._ClassName__pin`,
a transformation called *name mangling*.
The type checker does not model this rewriting,
so its report on the code below disagrees with what runs:

```python
# name_mangling.py
class Vault:
    def __init__(self) -> None:
        self._balance = 0
        self.__pin = "1234"

v = Vault()
print(vars(v))
#: {'_balance': 0, '_Vault__pin': '1234'}
# ty: unresolved attribute "_Vault__pin":
print(v._Vault__pin)  # type: ignore
#: 1234
```

Mangling exists to keep a base class's private-looking names apart from a subclass's names,
not to hide the attribute.
In Python the distinction between white-box and black-box remains one of discipline,
not of compiler enforcement.

That reliance on discipline makes black-box testing the sensible default.
If you test the public surface, the methods a caller should use,
the tests survive changes to the internals.
The `Account` tests are black-box.
They read `balance` and call the public methods.
When you do need a white-box test for a tricky internal,
Python lets you write one.
That test may break when you refactor the internals it reads.

## Isolating Tests from the World

Good tests stay independent of the real filesystem, environment,
random number generation, clock, and network.
`pytest` includes built-in fixtures for this.
`tmp_path` gives each test a private temporary directory.
`monkeypatch` sets and restores environment variables and attributes,
undoing every change when the test ends.

A function that prints writes to the terminal,
which is part of the world as well.
`contextlib.redirect_stdout()` is a context manager that points `sys.stdout` at another file object until its block ends,
so a test can collect the printed text in an `io.StringIO` and compare it:

```python
# test_printed_balance.py
import io
from contextlib import redirect_stdout
from account import Account

def report(account: Account) -> None:
    print(f"balance: {account.balance:.2f}")

def test_report_prints_balance() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        report(Account(100))
    assert buffer.getvalue() == "balance: 100.00\n"
```

`pytest`'s built-in `capsys` fixture captures the output of a whole test.
`capsys.readouterr().out` returns the text the test has printed so far.
`redirect_stdout()` limits the capture to its block,
and it works outside `pytest` as well.

### Filesystem and Environment

`save()` and `load()` write and read files in the directory that the `APP_DATA` environment variable names:

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

Python 3.15 makes UTF-8 the default encoding for `open()`, `Path.read_text()`,
and `Path.write_text()`, whatever the system locale,
so a test that writes and reads text gives the same result on every machine.
`storage.py` still passes `encoding="utf-8"` for code that must also run on Python 3.14 and earlier,
where the locale decides the encoding.

`Path()` keeps a leading `~` as written,
so a variable that may hold `~/data` needs `.expanduser()` on the result.

Python 3.14 added `Path.info`, which answers `exists()`, `is_dir()`,
`is_file()`, and `is_symlink()`.
`Path.info` caches each answer on the `Path` object the first time you ask,
so a test that changes the file afterward needs a fresh `Path`.

The `app_data()` fixture points `APP_DATA` at a throwaway directory before each test,
so each test works in its own empty directory,
apart from real data and from every other test:

```python
# test_storage.py
from pathlib import Path
import pytest
import storage

@pytest.fixture(autouse=True)
def app_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

def test_round_trip() -> None:
    storage.save("greeting.txt", "hello")
    assert storage.load("greeting.txt") == "hello"

def test_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        storage.load("absent.txt")
```

A fixture requests other fixtures the way a test does,
by naming them as parameters.

The value of `app_data()` is a side effect,
so `@pytest.fixture(autouse=True)` applies the fixture to both tests in `test_storage.py`,
whose parameter lists stay empty.

`data_dir()` reads `APP_DATA` on every call,
so the fixture's `monkeypatch.setenv()` can change the directory `data_dir()` returns.
A module-level `DATA_DIR = Path(os.environ.get("APP_DATA", "."))` reads the variable once,
at import time, before any fixture runs,
so the constant keeps that first value after the fixture patches the environment.
Reading a setting where you use it, rather than caching it at import,
is most of what makes a module testable.

### Random Numbers

Code that calls `random` produces a different value each run,
so a test cannot assert a known result:

```python
# dice.py
import random

def roll() -> int:
    return random.randint(1, 6)
```

`monkeypatch` replaces `randint()` with a *stub*,
a function that returns a known value,
so `roll()` returns that value while the test runs:

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
so `dice.random` and `random` are the same object.
The patch therefore replaces `randint()` process-wide.
`monkeypatch` restores the original when the test ends.
Because of that restoration, a later test calls the real `randint()`.

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

Because the function takes its source of randomness as an argument,
production code hands it a `random.Random()` seeded from the operating system,
while the test hands it `Random(0)`.
The randomness is now an input, not a hidden dependency.
This technique is *dependency injection*:
the caller hands the function its dependencies.
The function fetches nothing on its own.

The `4` in `test_dice_rng.py` is what `Random(0)` produces first.
Its match with the stubbed value in `test_dice.py` is a coincidence.
As with any seed, you record the value it gives you rather than pick one.

### The Clock

Code that reads `time.monotonic()` gives a different answer every run:

```python
# stopwatch.py
import time

def elapsed(start: float) -> float:
    return time.monotonic() - start
```

`time.monotonic()` is the clock for measuring an interval.
It keeps counting forward when someone resets the system clock,
while `time.time()` jumps with the reset.

`monkeypatch.setattr()` replaces `time.monotonic()` with a function that returns a known value,
as it replaced `randint()`:

```python
# test_stopwatch.py
import pytest
import stopwatch

def test_elapsed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stopwatch.time, "monotonic",
                        lambda: 100.0)
    assert stopwatch.elapsed(40.0) == 60.0
```

As with randomness, injecting the clock removes the patch.

```python
# stopwatch_clock.py
from collections.abc import Callable

def elapsed(start: float,
            now: Callable[[], float]) -> float:
    return now() - start
```

```python
# test_stopwatch_clock.py
import stopwatch_clock

def test_elapsed() -> None:
    assert stopwatch_clock.elapsed(
        40.0, lambda: 100.0) == 60.0
```

Both tests check the same arithmetic.
`test_stopwatch_clock.py` needs no `monkeypatch`,
because the `elapsed()` it tests takes its source of time as a parameter.

The `rng` or `now` parameter must appear on every function between the caller and the code that needs it.
When that code sits several calls deep in a real codebase,
you widen every signature along the way,
or introduce a context object to carry the parameter.
[Concurrency](19_Techniques--Concurrency.md#context-that-follows-the-call-chain)
shows `ContextVar`, which carries such a value down the call chain and leaves every signature as it was.
`monkeypatch` adds no parameters.
It patches the name in place,
and the patch applies process-wide until teardown restores the name.
Choose injection when the parameter sits near the boundary.
Choose `monkeypatch` when passing the parameter down changes more code than the test is worth.

`monkeypatch` cannot patch `datetime.now()`.
`monkeypatch.setattr(datetime, "now", ...)` raises a `TypeError`,
because `datetime` is an immutable C type that rejects attribute assignment.
That rejection justifies the effort of injection for code that calls `datetime.now()`.

If you cannot change the code,
the library [`time-machine`](https://github.com/adamchainz/time-machine)
sets every source of wall-clock time at once, including `datetime.now()`,
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
    assert datetime.now() == datetime.now()
```

`travel` sets the clock to the given moment for the test.
`tick=False` holds the clock there, so every reading is equal,
as `datetime.now() == datetime.now()` shows.
`time.monotonic()` and `time.perf_counter()` keep running,
because they measure elapsed intervals rather than dates.
`stopwatch.elapsed()` therefore keeps changing under `time-machine`.
Patching or injection still controls its result.

`monkeypatch` comes with `pytest`, and `time-machine` is a separate dependency.
Still, `time-machine` is the standard answer for code built around `datetime`.

### Network Calls

Keep tests off the real network.
A network call is slow, it fails whenever the service or the connection does,
and it makes the test depend on data someone else controls.
`monkeypatch` replaces the function that fetches data with one that returns a canned response,
so the test runs offline and gives the same answer every time.
Here, a function reads a URL:

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

`weather` imports the function with `from urllib.request import urlopen`.
That statement binds `urlopen` in `weather`'s own namespace,
so `weather.urlopen` is the name the call site reads and the name to patch.
Patching `urllib.request.urlopen` leaves `weather.urlopen` bound to the real function.
One rule covers both `import module` and `from module import name`:
patch the name the calling code looks up.

The same approach isolates a database, a message queue, or any other service.
Replace the boundary function with a stand-in,
and assert against what the calling code returns.

### Stubs and Mocks

A stand-in like `fake_urlopen()` is a stub.
It answers with a canned value and records nothing.
The standard library's `unittest.mock` appears in most existing test code.
It builds stubs for you, and it builds *mocks*.
A `Mock` goes further than a stub.
It records every call it receives,
so a test can check the call as well as what the call returned.

```python
# notifier.py
from collections.abc import Callable

def notify_negative_balance(
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
    notifier.notify_negative_balance(-5, send)
    send.assert_called_once_with(
        "balance is negative: -5")
```

`Mock()` accepts any call, records it, and returns its `return_value`,
which is another `Mock` by default.
`assert_called_once_with()` checks two things at once:
that `send` ran exactly once, and that it ran with this argument.
A stub such as `fake_urlopen()` records nothing about its calls,
so it cannot make that check.

A `Mock` accepts a call the real function rejects,
so a test keeps passing after the real signature changes.
`create_autospec()`, also in `unittest.mock`,
builds a mock from the real function and checks each call against the real function's signature.

This book patches with `monkeypatch` and prefers injection where you can change the code,
because a function that takes its clock or its fetcher as an argument needs no patching library.

## Property-Based Testing

The tests in this chapter check specific examples:
this input produces that output.
A *property-based* test states a law the code must always obey,
and lets a tool generate inputs that try to break it.
[Confidence](43_Functional--Confidence.md#property-based-testing)
shows the technique,
including the [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
library that automates it.

## Making Code Testable

To make an untested function testable, first name its dependencies: the clock,
randomness, the filesystem, the environment, the network.
Replace those at the boundary,
by injection where you can change the code and with `monkeypatch` where you cannot.
Then test what the function computes from its inputs with a handful of parametrized cases.
The work is mostly in the first two steps,
since a function that is hard to test usually fetches a dependency that a caller could pass in.

To find out what you have not tested, run the suite under `coverage.py`,
which the `pytest-cov` plugin runs when you pass `--cov`.
Read the result as a list of unexecuted lines, not as a score.
A line a test happened to execute differs from a line a test checks.

## Exercises

Try each exercise before opening its [solution](../Solutions/11_Techniques--Testing/).

1.  Add a `transfer(other: Account, amount: float)` method to `Account` and write its tests first:
    a successful transfer, and an overdraft that leaves both accounts unchanged.
2.  Use `parametrize` to test `add_interest()` at several rates,
    comparing with `pytest.approx()`.
3.  Write a fixture that `yield`s an `Account` and asserts, after the `yield`,
    that the balance is not negative.
    Use it in two tests.
4.  Write `settings_path()`,
    which returns `Path(os.environ["APP_CONFIG"]) / "settings.ini"`,
    and test it with `monkeypatch` and `tmp_path`.
    Then rewrite the function to take the directory as an argument and test it again.
    Which test survives a change to the environment variable's name?
5.  `weather.current_temp()` calls `urlopen()`.
    Write a second function that takes a fetcher as an argument instead,
    and test both: one with `monkeypatch`, one with a plain function passed in.
    Then rename `weather.urlopen` to `weather.fetch` and see which test still passes.
6.  `test_notifier.py` checks that a negative balance sends a message.
    Write the test for the other branch:
    a balance of zero or more sends nothing.
    Then write the same test with a hand-written stub in place of the `Mock`.
    What must the stub gain to make the check?

[^parametrize]: Four spellings are in use, all correct.
    The stem is `parametr-` or `parameter-`.
    The suffix is `-ize` in the US
    or `-ise` in the UK and Commonwealth countries.
    The two choices are independent,
    giving `parametrize`, `parametrise`, `parameterize`, and `parameterise`.
    This book follows pytest's own spelling, `parametrize`,
    for the mark and for the fixtures and tests it builds,
    and uses "parameterize" everywhere else,
    for the general sense of a class or function taking a parameter.

[^book-tests]: This book's own build extracts every listing,
    including this chapter's `test_*.py` and `conftest.py` files,
    and hands them to `pytest` instead of running them as plain programs.
    A failing test fails the build,
    the same way a failing type check or an unexpected exception does
    elsewhere in the book.
