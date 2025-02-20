from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..models.feature import Feature, FeatureValue, FeatureGroup
from ..services.feature_store import FeatureStore
from ..core.config import settings

router = APIRouter()
feature_store = FeatureStore()

@router.post("/", response_model=Feature)
async def create_feature(feature: Feature):
    """Create a new feature definition"""
    return await feature_store.create_feature(feature)

@router.get("/{feature_name}", response_model=Feature)
async def get_feature(feature_name: str):
    """Get feature by name"""
    feature = await feature_store.get_feature(feature_name)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

@router.post("/values/batch")
async def ingest_feature_values(values: List[FeatureValue]):
    """Ingest batch of feature values"""
    return await feature_store.ingest_feature_values(values)

@router.get("/values/{entity_key}")
async def get_feature_values(entity_key: str, features: List[str]):
    """Get feature values for an entity"""
    return await feature_store.get_feature_values(entity_key, features)

@router.post("/groups/", response_model=FeatureGroup)
async def create_feature_group(group: FeatureGroup):
    """Create a new feature group"""
    return await feature_store.create_feature_group(group)

@router.get("/groups/{group_name}", response_model=FeatureGroup)
async def get_feature_group(group_name: str):
    """Get feature group by name"""
    group = await feature_store.get_feature_group(group_name)
    if not group:
        raise HTTPException(status_code=404, detail="Feature group not found")
    return group

@router.post("/transform")
async def transform_features(
    feature_group: str,
    transformation: str,
    input_data: dict
):
    """Transform features using Spark"""
    return await feature_store.transform_features(
        feature_group,
        transformation,
        input_data
    )
