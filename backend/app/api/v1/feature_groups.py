"""API endpoints para grupos de features."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.store import get_store
from app.services.feature_store import FeatureStore
from app.models.feature_group import FeatureGroup, FeatureGroupCreate, FeatureGroupUpdate

router = APIRouter()

def get_store() -> FeatureStore:
    """Dependência para obter a instância do FeatureStore."""
    return get_store()

@router.post("/feature-groups", response_model=FeatureGroup)
async def create_feature_group(feature_group: FeatureGroupCreate, store: FeatureStore = Depends(get_store)):
    """Cria um novo grupo de features."""
    try:
        return await store.create_feature_group(feature_group)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/feature-groups", response_model=List[FeatureGroup])
async def list_feature_groups(
    skip: int = 0,
    limit: int = 10,
    entity_type: Optional[str] = None,
    tag: Optional[str] = None,
    status: Optional[str] = Query(None, enum=["active", "deprecated"]),
    store: FeatureStore = Depends(get_store)
):
    """Lista grupos de features com filtros opcionais."""
    try:
        return await store.list_feature_groups(
            skip=skip,
            limit=limit,
            entity_type=entity_type,
            tag=tag,
            status=status
        )
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

@router.put("/feature-groups/{group_id}", response_model=FeatureGroup)
async def update_feature_group(
    group_id: str,
    group_update: FeatureGroupUpdate,
    store: FeatureStore = Depends(get_store)
):
    """Atualiza um grupo de features."""
    try:
        group = await store.update_feature_group(group_id, group_update)
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

@router.get("/feature-groups/{group_id}/features")
async def get_group_features(group_id: str, store: FeatureStore = Depends(get_store)):
    """Lista todas as features de um grupo."""
    try:
        group = await store.get_feature_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Grupo não encontrado")
        features = await store.get_features_by_group(group_id)
        return features
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/feature-groups/{group_id}/statistics")
async def get_group_statistics(group_id: str, store: FeatureStore = Depends(get_store)):
    """Obtém estatísticas agregadas do grupo de features."""
    try:
        stats = await store.get_feature_group_statistics(group_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
