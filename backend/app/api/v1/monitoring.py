from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
from app.core.store import get_feature_store

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Verifica a saúde do sistema
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Retorna métricas e estatísticas sobre o Feature Store
    """
    try:
        feature_store = get_feature_store()
        if feature_store is None:
            raise HTTPException(status_code=500, detail="Feature store not initialized")

        # Obter todas as features e grupos
        features = await feature_store.list_features()
        feature_groups = await feature_store.list_feature_groups()
        
        # Calcular estatísticas
        total_features = len(features)
        total_groups = len(feature_groups)
        
        return {
            "total_features": total_features,
            "total_feature_groups": total_groups,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
