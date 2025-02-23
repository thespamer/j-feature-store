from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.feature import FeatureGroup
from app.core.store import get_feature_store

router = APIRouter()

@router.get("/")
async def get_feature_groups() -> List[Dict[str, Any]]:
    """
    Retorna todos os grupos de features
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")
        return await feature_store.list_feature_groups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_feature_group(group: FeatureGroup) -> FeatureGroup:
    """
    Cria um novo grupo de features
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")
        return await feature_store.create_feature_group(group)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
