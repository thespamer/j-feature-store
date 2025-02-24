import pytest
import asyncio
from app.core.store import initialize_store, get_feature_store

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_feature_store():
    """Initialize the feature store before all tests."""
    await initialize_store()
    store = get_feature_store()
    if store is None:
        raise RuntimeError("Feature store failed to initialize")
    yield store
