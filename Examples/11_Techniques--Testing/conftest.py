# conftest.py
import pytest
from account import Account

@pytest.fixture(scope="session")
def bank_name() -> str:
    return "Crunchy Frog Credit Union"

@pytest.fixture(params=[0.0, 100.0, 1_000_000.0])
def preloaded(request: pytest.FixtureRequest) -> Account:
    return Account(request.param)
