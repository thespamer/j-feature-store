from app.db.mongodb import get_database

async def get_db():
    """Get database connection."""
    return await get_database()
