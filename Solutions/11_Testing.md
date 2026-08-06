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
`test_add_interest_rates[0.05]`, and so on. `pytest.approx()` absorbs
the ordinary floating-point rounding in `100 * 1.05` versus
`100 + 100 * 0.05`, so the test checks the intended relationship
instead of exact bit-for-bit equality.

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
