# conftest.py
import pytest
from account import Account

@pytest.fixture(scope="session")
def bank_name() -> str:
    "Built once for the whole test session."
    return "Crunchy Frog Credit Union"

@pytest.fixture(params=[0.0, 100.0, 1_000_000.0])
def preloaded(request: pytest.FixtureRequest) -> Account:
    "Parametrized over starting balances. Tests run once per value."
    return Account(request.param)
