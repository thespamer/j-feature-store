from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from bson import ObjectId

from app.models.feature import Feature
from app.transformations.base import FeatureTransformer
from .version import FeatureVersion
from app.core.config import settings

class FeatureRegistry:
    """Central registry for managing features and their versions."""
    
    def __init__(self):
        self.mongodb = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.mongodb.get_database()
        self.redis = redis.from_url(settings.REDIS_URI)
        
    async def register_feature(self, feature: Feature, transformer: Optional[FeatureTransformer] = None) -> str:
        """Register a new feature with optional transformer."""
        version = "1.0.0"
        
        # Create version record
        feature_version = FeatureVersion(
            version=version,
            feature_id=feature.id,
            config=feature.model_dump(),
            transformer_config=transformer.get_config() if transformer else None,
            description=f"Initial version of feature {feature.name}"
        )
        
        # Save to MongoDB
        version_dict = feature_version.model_dump()
        await self.db.feature_versions.insert_one(version_dict)
        
        # Update feature with version info
        feature.metadata["current_version"] = version
        await self.db.features.update_one(
            {"_id": ObjectId(feature.id)},
            {"$set": {"metadata": feature.metadata}}
        )
        
        # Update Redis cache
        redis_key = f"feature:{feature.id}"
        await self.redis.set(redis_key, json.dumps(feature.model_dump()))
        
        return version
        
    async def get_feature_version(self, feature_id: str, version: Optional[str] = None) -> Optional[FeatureVersion]:
        """Get a specific version of a feature."""
        query = {"feature_id": feature_id}
        if version:
            query["version"] = version
        else:
            # Get latest version
            query["version"] = await self._get_latest_version(feature_id)
            
        doc = await self.db.feature_versions.find_one(query)
        return FeatureVersion(**doc) if doc else None
        
    async def list_feature_versions(self, feature_id: str) -> List[FeatureVersion]:
        """List all versions of a feature."""
        cursor = self.db.feature_versions.find({"feature_id": feature_id})
        versions = []
        async for doc in cursor:
            versions.append(FeatureVersion(**doc))
        return versions
        
    async def _get_latest_version(self, feature_id: str) -> Optional[str]:
        """Get the latest version of a feature."""
        doc = await self.db.feature_versions.find_one(
            {"feature_id": feature_id},
            sort=[("created_at", -1)]
        )
        return doc["version"] if doc else None
        
    async def update_feature_version(self, feature: Feature, transformer: Optional[FeatureTransformer] = None) -> str:
        """Create a new version of an existing feature."""
        current_version = feature.metadata.get("current_version")
        if not current_version:
            return await self.register_feature(feature, transformer)
            
        # Increment version
        major, minor, patch = map(int, current_version.split("."))
        new_version = f"{major}.{minor}.{patch + 1}"
        
        # Create new version record
        feature_version = FeatureVersion(
            version=new_version,
            feature_id=feature.id,
            config=feature.model_dump(),
            transformer_config=transformer.get_config() if transformer else None,
            description=f"Updated version of feature {feature.name}"
        )
        
        # Save to MongoDB
        version_dict = feature_version.model_dump()
        await self.db.feature_versions.insert_one(version_dict)
        
        # Update feature metadata
        feature.metadata["current_version"] = new_version
        await self.db.features.update_one(
            {"_id": ObjectId(feature.id)},
            {"$set": {"metadata": feature.metadata}}
        )
        
        # Update Redis cache
        redis_key = f"feature:{feature.id}"
        await self.redis.set(redis_key, json.dumps(feature.model_dump()))
        
        return new_version
