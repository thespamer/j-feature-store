from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def main():
    client = AsyncIOMotorClient('mongodb://mongodb:27017/fstore')
    db = client.get_database()
    cursor = db.feature_groups.find()
    async for doc in cursor:
        print(doc)
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
