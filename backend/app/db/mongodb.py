"""MongoDB database connection."""
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

_client = None
_db = None

async def get_database():
    """Get database connection."""
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
        _db = _client[settings.MONGODB_DB]
    return _db

async def close_database():
    """Close database connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
