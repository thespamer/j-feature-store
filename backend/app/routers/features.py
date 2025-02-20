from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

from app.models.feature import Feature, FeatureGroup, FeatureValue
from app.services.feature_store import FeatureStore

router = APIRouter()
feature_store = FeatureStore()

@router.post("/features", response_model=Feature)
async def create_feature(feature: Feature):
    """Create a new feature in the feature store"""
    return await feature_store.create_feature(feature)

@router.get("/features/{feature_id}", response_model=Feature)
async def get_feature(feature_id: str):
    """Get a specific feature by ID"""
    feature = await feature_store.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

@router.get("/features", response_model=List[Feature])
async def list_features(entity_id: Optional[str] = None):
    """List all features, optionally filtered by entity ID"""
    return await feature_store.list_features(entity_id)

@router.post("/feature-groups", response_model=FeatureGroup)
async def create_feature_group(group: FeatureGroup):
    """Create a new feature group"""
    return await feature_store.create_feature_group(group)

@router.get("/feature-groups/{group_id}", response_model=FeatureGroup)
async def get_feature_group(group_id: str):
    """Get a specific feature group by ID"""
    group = await feature_store.get_feature_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Feature group not found")
    return group

@router.get("/feature-groups", response_model=List[FeatureGroup])
async def list_feature_groups():
    """List all feature groups"""
    return await feature_store.list_feature_groups()

@router.post("/features/{feature_id}/values")
async def store_feature_value(feature_id: str, value: FeatureValue):
    """Store a new value for a feature"""
    feature = await feature_store.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    await feature_store.store_feature_value(feature_id, value)
    return {"status": "success"}

@router.get("/features/{feature_id}/latest", response_model=float)
async def get_latest_value(feature_id: str):
    """Get the latest value for a feature"""
    feature = await feature_store.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    value = await feature_store.get_latest_feature_value(feature_id)
    if value is None:
        raise HTTPException(status_code=404, detail="No values found for this feature")
    return value

@router.get("/features/{feature_id}/history", response_model=List[FeatureValue])
async def get_feature_history(
    feature_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """Get historical values for a feature"""
    feature = await feature_store.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return await feature_store.get_feature_history(feature_id, start_time, end_time)
