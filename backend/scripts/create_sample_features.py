import asyncio
import aiohttp
import json

async def create_feature(session, feature_data):
    async with session.post('http://localhost:8000/api/v1/features/', json=feature_data) as response:
        return await response.json()

async def main():
    sample_features = [
        {
            "name": "total_purchases",
            "description": "Total de compras do cliente",
            "feature_group_id": "67ba0df0c119395cdeed4002",
            "type": "float",
            "entity_id": "customer",
            "tags": ["financial", "customer"]
        },
        {
            "name": "average_ticket",
            "description": "Ticket médio do cliente",
            "feature_group_id": "67ba0df0c119395cdeed4002",
            "type": "float",
            "entity_id": "customer",
            "tags": ["financial", "customer"]
        },
        {
            "name": "last_purchase_date",
            "description": "Data da última compra",
            "feature_group_id": "67ba0df0c119395cdeed4002",
            "type": "datetime",
            "entity_id": "customer",
            "tags": ["temporal", "customer"]
        }
    ]

    async with aiohttp.ClientSession() as session:
        for feature in sample_features:
            try:
                result = await create_feature(session, feature)
                print(f"Created feature: {result}")
            except Exception as e:
                print(f"Error creating feature {feature['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
