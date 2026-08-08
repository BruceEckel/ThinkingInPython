# Testing: Solutions

## 1. `transfer()`, tests written first

```python
# test_ch11_transfer.py
import pytest

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

    def transfer(self, other: Account, amount: float) -> None:
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

`transfer()` calls `self.withdraw(amount)` before `other.deposit(amount)`.
`withdraw()` checks the balance and raises `InsufficientFunds` *before*
touching `self.balance`, so an overdrafting transfer never reaches the
`deposit()` call at all: both accounts are left exactly as they were.
Writing the overdraft test first makes this ordering a
deliberate decision rather than an accident; a version that deposits
first and withdraws second leaves `other` credited even when the
transfer as a whole should fail.

## 2. Parametrized interest rates

```python
# test_ch11_interest_rates.py
import pytest

class Account:
    def __init__(self, balance: float = 0.0) -> None:
        self.balance = balance

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
def test_add_interest_rates(funded: Account, rate: float) -> None:
    funded.add_interest(rate)
    assert funded.balance == pytest.approx(100 * (1 + rate))
```

`parametrize` runs this one test body four times, once per rate,
reported individually as `test_add_interest_rates[0.0]`,
`test_add_interest_rates[0.05]`, and so on. `pytest.approx()` is here
because the relationship the test states is not guaranteed to be
exact, not because these four rates round. For `0.0`, `0.05`, `0.5`,
and `1.0` on a balance of `100`, the two forms are bit-identical and
`==` would pass just as well. A rate that does not land on a binary
fraction, or interest applied more than once, is where the assertion
needs the tolerance.

## 3. A fixture asserting an invariant after the test

```python
# test_ch11_invariant.py
import pytest

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

@pytest.fixture
def never_negative():
    account = Account()
    account.deposit(50)
    yield account
    assert account.balance >= 0

def test_never_negative_after_partial_withdraw(
    never_negative: Account,
) -> None:
    never_negative.withdraw(20)

def test_never_negative_after_deposit(
    never_negative: Account,
) -> None:
    never_negative.deposit(10)
```

Code after a fixture's `yield` runs as teardown, once the test function
that used the fixture finishes, whether it passed or raised. Here that
teardown is itself an assertion, so it doubles as a check: no matter
what either test does to the account, `never_negative`'s balance must
still be non-negative once the test body returns control to the
fixture. Both tests pass the same shared invariant check with no
duplicated assertion in either test body.

## 4. The environment variable, patched and then injected

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
    assert settings.settings_path() == tmp_path / "settings.ini"

def test_settings_path_in_takes_the_directory(tmp_path: Path) -> None:
    expected = tmp_path / "settings.ini"
    assert settings.settings_path_in(tmp_path) == expected
```

The first test has to know two things about the implementation: that
the function reads an environment variable, and that the variable is
spelled `APP_CONFIG`. Renaming it to `APP_SETTINGS_DIR` breaks the
test even though the behavior is unchanged, and the failure is a
`KeyError` from inside the function rather than a message about the
name. The second test knows only what the function promises: give it a
directory, get the settings file inside it. That test survives the
rename, and it survives dropping the environment variable entirely.

`tmp_path` is still worth taking in the second test, even though
nothing touches the disk, because it supplies a real, valid path
without hard-coding one that would differ across operating systems.

The trade is that injection moves the decision outward: somebody has
to read `APP_CONFIG` and pass the directory in. That somebody is
usually one function at the program's edge, which is the one place a
patching test is worth writing.

## 5. Stubbing a boundary, patched and then injected

```python
# ch11_weather.py
import io
from collections.abc import Callable
from urllib.request import urlopen

def current_temp(city: str) -> str:
    with urlopen(f"https://example.com/{city}") as response:
        return response.read().decode()

def current_temp_with(
    city: str, fetch: Callable[[str], io.IOBase]
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
    got = ch11_weather.current_temp_with("denver", fake_fetch)
    assert got == "21C"
```

Both tests pass and neither touches the network. The stub is the same
function in both: a fetcher returning a `BytesIO` that behaves enough
like a response to satisfy the `with` block and `.read()`.

Renaming `urlopen` to `fetch` in `ch11_weather.py` separates them.
`test_injected()` still passes, because it never named the dependency;
it hands one in, and `current_temp_with()` calls whatever it was
given. `test_patched()` fails with
`AttributeError: <module 'ch11_weather'> has no attribute 'urlopen'`,
because `monkeypatch.setattr()` looks the name up by string and the
string is now wrong.

That is the same lesson exercise 4 draws from the environment variable,
applied to a different kind of dependency. A patched test is coupled to
the *name* of the thing it replaces, in the module where that name
lives. An injected test is coupled only to the shape of what it passes.
Rename the import, move the call to a helper, or import `urlopen` a
different way, and the patched test breaks while the code still works.

`monkeypatch` earns its place where you cannot change the code:
someone else's library, or a function you are not ready to refactor.
Where you can change the signature, injection turns the dependency into
part of the contract, which is what the chapter means by a function
that goes looking for something it was never handed.
