# Testing: Solutions

## 1. `transfer()`, tests written first

> Add a `transfer(other: Account, amount: float)` method to `Account` and write its tests first:
> a successful transfer, and an overdraft that leaves both accounts unchanged.

<details>
<summary>Where to look</summary>

[Test-Driven Development (TDD)](../../Chapters/11_Techniques--Testing.md#test-driven-development-tdd)
has you write the failing test before the code that satisfies it.
Write both tests first,
then build `transfer()` from the existing `withdraw()` and `deposit()` methods.
The order of those two calls decides whether the other account keeps its balance when a transfer fails.
The overdraft test checks the failing transfer with `pytest.raises()`,
as in [Testing for Exceptions](../../Chapters/11_Techniques--Testing.md#testing-for-exceptions).

<details>
<summary>Done when</summary>

both tests fail with `AttributeError` before you write `transfer()`,
and `uv run pytest` passes them after.
A `transfer()` that changes `other` before it checks the balance fails your overdraft test on `other.balance`.

<details>
<summary>Solution</summary>

If you deposit first and withdraw second,
`other` keeps the deposit when the transfer as a whole should fail.
The overdraft test then fails with `assert 1000.0 == 0` on `other.balance`.
The solution withdraws first,
so `withdraw()` checks the balance before either account changes.

```python
# test_ch11_transfer.py
from dataclasses import dataclass
import pytest

class InsufficientFunds(Exception):
    def __init__(self, balance: float,
                 amount: float) -> None:
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

    def transfer(self, other: Account,
                 amount: float) -> None:
        self.withdraw(amount)
        other.deposit(amount)

@pytest.fixture
def funded() -> Account:
    account = Account()
    account.deposit(100)
    return account

def test_transfer_moves_balance(funded: Account) -> None:
    other = Account()
    funded.transfer(other, 40)
    assert funded.balance == 60
    assert other.balance == 40

def test_transfer_overdraft_leaves_both_unchanged(
    funded: Account,
) -> None:
    other = Account()
    with pytest.raises(InsufficientFunds):
        funded.transfer(other, 1000)
    assert funded.balance == 100
    assert other.balance == 0
```

**Fail before changing either account.**
`withdraw()` checks the balance and raises `InsufficientFunds` before touching `self.balance`,
so an overdrafting transfer stops before the `deposit()` call.

**Pin the order with a test.**
Writing the overdraft test first makes this ordering a deliberate decision rather than an accident.
A later edit that swaps the two calls fails the same test.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 2. Parametrized interest rates

> Use `parametrize` to test `add_interest()` at several rates,
> comparing with `pytest.approx()`.

<details>
<summary>Where to look</summary>

[Parametrizing Tests](../../Chapters/11_Techniques--Testing.md#parametrizing-tests)
shows `@pytest.mark.parametrize` running one test body once per value.
Pass the rates as a list and take `rate` as a test parameter.
Compare the balance using `pytest.approx()`,
which [Comparing Floating-Point Values](../../Chapters/11_Techniques--Testing.md#comparing-floating-point-values)
introduces.

<details>
<summary>Done when</summary>

`uv run pytest -v` lists one passing test per rate, each ID ending in its rate,
such as `[0.05]`.
Adding `0.1` to your rates still passes,
and that `0.1` case fails if you replace `pytest.approx()` with a bare `==`.

<details>
<summary>Solution</summary>

```python
# test_ch11_interest_rates.py
from dataclasses import dataclass
import pytest

@dataclass
class Account:
    balance: float = 0.0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def add_interest(self, rate: float) -> None:
        self.balance += self.balance * rate

@pytest.fixture
def funded() -> Account:
    account = Account()
    account.deposit(100)
    return account

@pytest.mark.parametrize("rate", [0.0, 0.05, 0.5, 1.0])
def test_add_interest_rates(funded: Account,
                            rate: float) -> None:
    funded.add_interest(rate)
    assert funded.balance == pytest.approx(100 * (1 + rate))
```

**Run one body per rate.**
`parametrize` runs this one test body four times, once per rate,
and `pytest` reports each run as `test_add_interest_rates[0.0]`,
`test_add_interest_rates[0.05]`, and so on.

**Allow for rounding.**
The method computes `100 + 100 * rate`, and the test expects `100 * (1 + rate)`.
Those two expressions can round differently,
so the test compares them with `pytest.approx()`.
For `0.0`, `0.05`, `0.5`, and `1.0` on a balance of `100`,
the two sides are bit-identical, so `==` passes just as well.
The assertion needs the tolerance for a rate such as `0.1`,
where the two sides differ by one bit, or for interest applied more than once.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. A fixture asserting an invariant after the test

> Write a fixture that `yield`s an `Account` and asserts, after the `yield`,
> that the balance is not negative.
> Use it in two tests.

<details>
<summary>Where to look</summary>

[Fixtures Replace Setup and Teardown](../../Chapters/11_Techniques--Testing.md#fixtures-replace-setup-and-teardown)
shows a fixture that `yield`s its value, with teardown code after the `yield`.
Create and fund the `Account` before the `yield`,
and put the `assert` on its balance after the `yield`.
Annotate the fixture as returning an `Iterator[Account]`,
then name it as a parameter in two tests.

<details>
<summary>Done when</summary>

both tests pass, and a third test that sets the account's `balance` to `-1` appears in the `pytest` report as `ERROR at teardown`,
rather than as a failure, with your fixture's balance assertion as the cause.

<details>
<summary>Solution</summary>

```python
# test_ch11_invariant.py
from collections.abc import Iterator
from dataclasses import dataclass
import pytest

class InsufficientFunds(Exception):
    def __init__(self, balance: float,
                 amount: float) -> None:
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

@pytest.fixture
def never_negative() -> Iterator[Account]:
    account = Account()
    account.deposit(50)
    yield account
    assert account.balance >= 0

def test_never_negative_after_full_withdraw(
    never_negative: Account,
) -> None:
    never_negative.withdraw(50)  # Down to exactly zero

def test_never_negative_after_deposit(
    never_negative: Account,
) -> None:
    never_negative.deposit(10)
```

**Check the invariant at teardown.**
Code after a fixture's `yield` runs as teardown,
once the test function that uses the fixture finishes,
whether it passes or raises an exception.
Whatever either test does to the account,
the balance must be zero or more once the test body returns control to the fixture.

**Share the check across tests.**
Both tests get the same invariant check from one assertion in the fixture.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. The environment variable, patched and then injected

> Write `settings_path()`,
> which returns `Path(os.environ["APP_CONFIG"]) / "settings.ini"`,
> and test it with `monkeypatch` and `tmp_path`.
> Then rewrite the function to take the directory as an argument and test it again.
> Which test survives a change to the environment variable's name?

<details>
<summary>Where to look</summary>

[Filesystem and Environment](../../Chapters/11_Techniques--Testing.md#filesystem-and-environment)
pairs `monkeypatch.setenv()` with the `tmp_path` fixture.
Use both to test `settings_path()`,
then write a second function that takes the directory as a parameter and test it with `tmp_path` alone.
To answer the question,
rename the variable in `settings_path()` and see which test still passes.

<details>
<summary>The shape</summary>

```python
# The shape of settings.py
import os
from pathlib import Path

def settings_path() -> Path:
    ...

def settings_path_in(directory: Path) -> Path:
    ...
```

<details>
<summary>Done when</summary>

both tests pass, and renaming `APP_CONFIG` inside `settings_path()` fails one of them with a `KeyError` that names the new variable while the other still passes.
You can name the fact about the implementation on which the failing test depends.

<details>
<summary>Solution</summary>

```python
# settings.py
import os
from pathlib import Path

def settings_path() -> Path:
    return Path(os.environ["APP_CONFIG"]) / "settings.ini"

def settings_path_in(directory: Path) -> Path:
    return directory / "settings.ini"
```

```python
# test_ch11_settings.py
from pathlib import Path
import pytest
import settings

def test_settings_path_reads_the_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_CONFIG", str(tmp_path))
    assert (settings.settings_path()
            == tmp_path / "settings.ini")

def test_settings_path_in_takes_the_directory(
    tmp_path: Path,
) -> None:
    expected = tmp_path / "settings.ini"
    assert settings.settings_path_in(tmp_path) == expected
```

**Supply the directory through the environment.**
The first test depends on two facts about the implementation:
that the function reads an environment variable,
and that the variable's name is `APP_CONFIG`.
Renaming the variable to `APP_SETTINGS_DIR` breaks the test although the function still works.
The failure is a `KeyError: 'APP_SETTINGS_DIR'` raised inside the function.
Its message names the variable the function now reads,
not the `APP_CONFIG` the test set.

**Supply the directory as an argument.**
The second test depends on one fact about behavior: given a directory,
the function returns the settings file inside it.
That test survives the rename,
and it survives a program that drops the environment variable.

The second test takes `tmp_path` as well,
although `settings_path_in()` never touches the disk.
`tmp_path` supplies a real, valid path,
where a hard-coded one differs across operating systems.

Injection moves the environment lookup out of the function and into a caller.
That caller must read `APP_CONFIG` and pass in the directory.
It is usually one function at the program's edge,
and that function is the one place a patching test is worth writing.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. Stubbing a boundary, patched and then injected

> `weather.current_temp()` calls `urlopen()`.
> Write a second function that takes a fetcher as an argument instead,
> and test both: one with `monkeypatch`, one with a plain function passed in.
> Then rename `weather.urlopen` to `weather.fetch` and see which test still passes.

<details>
<summary>Where to look</summary>

[Network Calls](../../Chapters/11_Techniques--Testing.md#network-calls)
replaces `urlopen()` with `monkeypatch.setattr()` so the test opens no network connection.
For the second function, accept a `Callable` that opens the URL,
and pass a plain function returning an `io.BytesIO`.
Both tests can share that one stub.
The rename shows how each test refers to the function it replaces.

<details>
<summary>The shape</summary>

```python
# The shape of ch11_weather.py
import io
from collections.abc import Callable
from urllib.request import urlopen

def current_temp(city: str) -> str:
    ...

def current_temp_with(
    city: str,
    fetch: Callable[[str], io.BufferedIOBase],
) -> str:
    ...
```

<details>
<summary>Done when</summary>

both tests pass with the network disconnected.
Renaming `urlopen` to `fetch` in your `weather` module fails the `monkeypatch` test with `AttributeError: ... has no attribute 'urlopen'` and leaves the injected test passing.

<details>
<summary>Solution</summary>

If you patch `urllib.request.urlopen` instead of `ch11_weather.urlopen`,
`current_temp()` still calls the real `urlopen()`,
because `from urllib.request import urlopen` binds the name in `ch11_weather`'s own namespace at import.
The test then tries to open a real connection to `example.com`.
The solution patches the name that `current_temp()` looks up.

```python
# ch11_weather.py
import io
from collections.abc import Callable
from urllib.request import urlopen

def current_temp(city: str) -> str:
    with urlopen(f"https://example.com/{city}") as response:
        return response.read().decode()

def current_temp_with(
    city: str,
    fetch: Callable[[str], io.BufferedIOBase],
) -> str:
    with fetch(f"https://example.com/{city}") as response:
        return response.read().decode()
```

```python
# test_ch11_weather.py
import io
import ch11_weather
import pytest

def fake_fetch(url: str) -> io.BytesIO:
    return io.BytesIO(b"21C")

def test_patched(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ch11_weather, "urlopen", fake_fetch)
    assert ch11_weather.current_temp("denver") == "21C"

def test_injected() -> None:
    got = ch11_weather.current_temp_with(
        "denver", fake_fetch)
    assert got == "21C"
```

**Answer with a canned response.**
Both tests pass, and neither opens a network connection.
The stub is the same function in both: a fetcher returning a `BytesIO`,
which works in the `with` block and answers `.read()` as a response does.

**Replace the dependency by name.**
Renaming `urlopen` to `fetch` in `ch11_weather.py` makes one test fail and leaves the other passing.
`test_patched()` fails with `AttributeError: <module 'ch11_weather' from '...'> has no attribute 'urlopen'`,
because `monkeypatch.setattr()` looks the name up by string and the string is now wrong.

**Pass the dependency in.**
`test_injected()` still passes,
because it hands the dependency in instead of naming it,
and `current_temp_with()` calls the fetcher it receives.

Exercise 4 draws the same lesson from the environment variable.
Here the dependency is a function.
A patched test depends on the name of the function it replaces,
in the module where that name lives.
So a patched test breaks under changes that leave `current_temp()` working:
renaming the import, moving the call into a helper module,
or importing `urlopen` a different way.
An injected test depends only on the shape of what it passes.

Use `monkeypatch` on code you must leave as it is: someone else's library,
or a function you mean to refactor later.
Where you can change the signature,
injection turns the dependency into part of the contract.
The function then receives what it needs from its caller.
A function that is [hard to test](../../Chapters/11_Techniques--Testing.md#making-code-testable)
usually does the opposite.
It fetches a dependency instead of accepting it as a parameter.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. The branch that sends nothing

> `test_notifier.py` checks that a negative balance sends a message.
> Write the test for the other branch:
> a balance of zero or more sends nothing.
> Then write the same test with a hand-written stub in place of the `Mock`.
> What must the stub gain to make the check?

<details>
<summary>Where to look</summary>

[Stubs and Mocks](../../Chapters/11_Techniques--Testing.md#stubs-and-mocks)
checks a call with a `Mock`, and `assert_not_called()` checks the opposite case.
Test a balance of zero as well as a positive one,
since zero is where the boundary lies.
Use `parametrize` to cover both.
A hand-written stub needs somewhere to keep what it receives,
so the test has something to inspect afterward.

<details>
<summary>Done when</summary>

your `Mock` test and your stub test each pass at balances `0` and `50`.
Changing `balance < 0` to `balance <= 0` in `notify_negative_balance()` fails the zero case of both tests,
and a version that sends on every call fails your stub test too.

<details>
<summary>Solution</summary>

If you test only a positive balance,
both tests pass with a mistaken `balance <= 0` in `notify_negative_balance()`,
because at `50` both comparisons are false.
`<` and `<=` disagree at one balance, zero,
so the solution adds `0` to the `parametrize` list.
With the mistaken `<=`, both zero cases fail.

```python
# test_ch11_silent_notifier.py
from collections.abc import Callable
from unittest.mock import Mock
import pytest

def notify_negative_balance(
    balance: float,
    send: Callable[[str], None],
) -> None:
    if balance < 0:
        send(f"balance is negative: {balance}")

@pytest.mark.parametrize("balance", [0, 50])
def test_mock_not_called(balance: float) -> None:
    send = Mock()
    notify_negative_balance(balance, send)
    send.assert_not_called()

@pytest.mark.parametrize("balance", [0, 50])
def test_stub_not_called(balance: float) -> None:
    sent: list[str] = []
    def send(message: str) -> None:
        sent.append(message)
    notify_negative_balance(balance, send)
    assert sent == []
```

**Check the silence with a mock.**
`assert_not_called()` fails if `send` received any call,
so a mistaken `<=` that sends at zero fails the zero case.

**Record the calls in the stub.**
A stub like exercise 5's `fake_fetch()` answers each call and forgets it.
A test with a `send` stub built that way passes whether or not `send` runs,
including against a `notify_negative_balance()` that always sends.
To make the check, the stub must gain a record of its calls.
Here that record is the list `sent`.

A stub that records its calls is a mock you write yourself.
`Mock` builds that recording for you, along with the assertions that read it.

The hand-written stub declares its signature, `(message: str) -> None`,
so the type checker verifies it against `Callable[[str], None]` and reports a type error when the two stop matching.
A `Mock` accepts any call.
`create_autospec()`, which the chapter introduces,
builds a mock that checks each call against the real function's signature.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
