"""API endpoints para grupos de features."""
from fastapi import APIRouter, HTTPException, Depends
from app.models.feature_group import FeatureGroup, FeatureGroupCreate
from app.services.feature_store import FeatureStore
from typing import List
from app.core.store import get_feature_store

router = APIRouter()

def get_store() -> FeatureStore:
    """Dependência para obter a instância do FeatureStore."""
    return get_feature_store()

@router.post("/feature-groups/", response_model=FeatureGroup)
async def create_feature_group(feature_group: FeatureGroupCreate, store: FeatureStore = Depends(get_store)):
    """Cria um novo grupo de features."""
    try:
        return await store.create_feature_group(feature_group)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/feature-groups/", response_model=List[FeatureGroup])
async def list_feature_groups(store: FeatureStore = Depends(get_store)):
    """Lista todos os grupos de features."""
    try:
        return await store.list_feature_groups()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/feature-groups/{group_id}", response_model=FeatureGroup)
async def get_feature_group(group_id: str, store: FeatureStore = Depends(get_store)):
    """Obtém um grupo de features pelo ID."""
    try:
        group = await store.get_feature_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Grupo não encontrado")
        return group
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/feature-groups/{group_id}")
async def delete_feature_group(group_id: str, store: FeatureStore = Depends(get_store)):
    """Remove um grupo de features."""
    try:
        await store.delete_feature_group(group_id)
        return {"message": "Grupo removido com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
