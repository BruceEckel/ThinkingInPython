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
Writing the overdraft test first is what makes this ordering a
deliberate decision rather than an accident; a version that deposited
first and withdrew second would leave `other` credited even when the
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
