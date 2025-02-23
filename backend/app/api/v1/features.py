from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app.models.feature import Feature, FeatureValue, FeatureCreate
from app.core.store import get_feature_store

router = APIRouter()

@router.post("/", response_model=Feature)
async def create_feature(feature_data: FeatureCreate):
    """
    Cria uma nova feature
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")
        feature = Feature(**feature_data.dict())
        return await feature_store.create_feature(feature)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Feature])
async def list_features(entity_id: Optional[str] = Query(None)):
    """
    Lista todas as features
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")
        return await feature_store.list_features(entity_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{feature_id}", response_model=Feature)
async def get_feature(feature_id: str):
    """
    Retorna uma feature específica
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")
        feature = await feature_store.get_feature(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")
        return feature
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{feature_id}/values", response_model=FeatureValue)
async def store_feature_value(feature_id: str, value: FeatureValue):
    """
    Armazena um valor de feature
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")
        return await feature_store.store_feature_value(feature_id, value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{feature_id}/values/{entity_id}", response_model=FeatureValue)
async def get_feature_value(feature_id: str, entity_id: str):
    """
    Retorna o último valor de uma feature para uma entidade
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")
        value = await feature_store.get_feature_value(feature_id, entity_id)
        if not value:
            raise HTTPException(status_code=404, detail="Feature value not found")
        return value
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
