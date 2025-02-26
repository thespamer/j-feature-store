"""API endpoints para features."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.feature import Feature, FeatureValue, FeatureCreate
from app.services.feature_store import FeatureStore, FeatureNotFoundError, ValidationError
from app.core.store import get_feature_store

router = APIRouter()

def get_store() -> FeatureStore:
    """Dependência para obter a instância do FeatureStore."""
    return get_feature_store()

@router.post("/features/", response_model=Feature, status_code=status.HTTP_201_CREATED)
async def create_feature(feature: FeatureCreate, store: FeatureStore = Depends(get_store)):
    """Cria uma nova feature."""
    try:
        return await store.create_feature(feature)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validação: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao criar feature: {str(e)}"
        )

@router.get("/features/", response_model=List[Feature])
async def list_features(store: FeatureStore = Depends(get_store)):
    """Lista todas as features."""
    try:
        return await store.list_features()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar features: {str(e)}"
        )

@router.get("/features/{feature_id}", response_model=Feature)
async def get_feature(feature_id: str, store: FeatureStore = Depends(get_store)):
    """Obtém uma feature pelo ID."""
    try:
        feature = await store.get_feature(feature_id)
        if not feature:
            raise FeatureNotFoundError(f"Feature {feature_id} não encontrada")
        return feature
    except FeatureNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar feature: {str(e)}"
        )

@router.delete("/features/{feature_id}")
async def delete_feature(feature_id: str, store: FeatureStore = Depends(get_store)):
    """Remove uma feature."""
    try:
        await store.delete_feature(feature_id)
        return {"message": "Feature removida com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover feature: {str(e)}"
        )

@router.post("/features/{feature_id}/values", response_model=FeatureValue)
async def insert_feature_value(
    feature_id: str,
    value: FeatureValue,
    store: FeatureStore = Depends(get_store)
):
    """Insere um valor para uma feature."""
    try:
        return await store.insert_feature_value(feature_id, value)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validação: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao inserir valor de feature: {str(e)}"
        )

@router.get("/features/{feature_id}/values", response_model=List[FeatureValue])
async def get_feature_values(
    feature_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    store: FeatureStore = Depends(get_store)
):
    """Obtém valores de uma feature."""
    try:
        return await store.get_feature_values(feature_id, start_time, end_time)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar valores de feature: {str(e)}"
        )
