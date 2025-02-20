from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
from bson import ObjectId
from app.models.feature import Feature, FeatureGroup, FeatureValue
from app.core.config import settings

class FeatureStore:
    def __init__(self):
        self.mongodb = AsyncIOMotorClient(settings.MONGODB_URI)
        self.redis = Redis.from_url(settings.REDIS_URI)
        self.db = self.mongodb.fstore
        
    async def create_feature(self, feature: Feature) -> Feature:
        feature_dict = feature.dict(exclude={'id'})
        result = await self.db.features.insert_one(feature_dict)
        feature.id = str(result.inserted_id)
        return feature
        
    async def get_feature(self, feature_id: str) -> Optional[Feature]:
        try:
            result = await self.db.features.find_one({"_id": ObjectId(feature_id)})
            if result:
                result['id'] = str(result.pop('_id'))
                return Feature(**result)
            return None
        except:
            return None
        
    async def list_features(self, entity_id: Optional[str] = None) -> List[Feature]:
        query = {"entity_id": entity_id} if entity_id else {}
        cursor = self.db.features.find(query)
        features = []
        async for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            features.append(Feature(**doc))
        return features
        
    async def create_feature_group(self, group: FeatureGroup) -> FeatureGroup:
        group_dict = group.dict(exclude={'id'})
        result = await self.db.feature_groups.insert_one(group_dict)
        group.id = str(result.inserted_id)
        return group
        
    async def get_feature_group(self, group_id: str) -> Optional[FeatureGroup]:
        try:
            result = await self.db.feature_groups.find_one({"_id": ObjectId(group_id)})
            if result:
                result['id'] = str(result.pop('_id'))
                return FeatureGroup(**result)
            return None
        except:
            return None
        
    async def list_feature_groups(self) -> List[FeatureGroup]:
        cursor = self.db.feature_groups.find()
        groups = []
        async for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            groups.append(FeatureGroup(**doc))
        return groups
        
    async def store_feature_value(self, feature_id: str, value: FeatureValue):
        # Store in Redis for fast access
        key = f"feature:{feature_id}:latest"
        self.redis.set(key, str(value.value))
        self.redis.expire(key, 3600)  # expire in 1 hour
        
        # Store in MongoDB for historical data
        await self.db.feature_values.insert_one({
            "feature_id": feature_id,
            "value": value.value,
            "timestamp": value.timestamp
        })
        
    async def get_latest_feature_value(self, feature_id: str) -> Optional[float]:
        # Try Redis first
        key = f"feature:{feature_id}:latest"
        value = self.redis.get(key)
        if value:
            return float(value)
            
        # Fall back to MongoDB
        result = await self.db.feature_values.find_one(
            {"feature_id": feature_id},
            sort=[("timestamp", -1)]
        )
        return float(result["value"]) if result else None
        
    async def get_feature_history(
        self, 
        feature_id: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[FeatureValue]:
        query = {"feature_id": feature_id}
        if start_time:
            query["timestamp"] = {"$gte": start_time}
        if end_time:
            query["timestamp"] = {"$lte": end_time}
            
        cursor = self.db.feature_values.find(query).sort("timestamp", -1)
        values = []
        async for doc in cursor:
            values.append(FeatureValue(
                value=doc["value"],
                timestamp=doc["timestamp"]
            ))
        return values
