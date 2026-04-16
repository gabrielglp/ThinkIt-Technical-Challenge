import pytest
from fastapi.testclient import TestClient

from app.core.limiter import limiter
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_rate_limits() -> None:
    """Reset in-memory rate limit counters before each test."""
    limiter._limiter.storage.reset()
