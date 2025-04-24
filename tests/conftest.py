import pytest
from fastapi.testclient import TestClient
from main import app
import redis_client

# Override Redis dependency with fresh in-memory store per test
default_store = None


@pytest.fixture(autouse=True)
def override_redis_store():
    store = redis_client.InMemoryStore()
    store._store['tx:id_counter'] = 0

    async def get_store():
        return store
    app.dependency_overrides[redis_client.get_redis] = get_store
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
