from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
from app.core.store import get_feature_store

router = APIRouter()

async def check_connections() -> Dict[str, Any]:
    """
    Verifica todas as conexões do sistema
    """
    feature_store = get_feature_store()
    if feature_store is None:
        return {"status": "error", "message": "Feature store not initialized"}
    
    status = {
        "mongodb": "healthy",
        "redis": "healthy",
        "overall": "healthy"
    }
    
    try:
        # Check MongoDB
        await feature_store.db.command('ping')
    except Exception as e:
        status["mongodb"] = f"unhealthy: {str(e)}"
        status["overall"] = "unhealthy"
    
    try:
        # Check Redis
        await feature_store.redis.ping()
    except Exception as e:
        status["redis"] = f"unhealthy: {str(e)}"
        status["overall"] = "unhealthy"
    
    return status

@router.get("/")
@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Verifica a saúde do sistema
    """
    try:
        status = await check_connections()
        return {
            **status,
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

        # Check connections first
        status = await check_connections()
        if status["overall"] != "healthy":
            raise HTTPException(status_code=500, detail=f"Unhealthy system state: {status}")

        # Obter todas as features e grupos
        features = await feature_store.list_features()
        feature_groups = await feature_store.db.feature_groups.find().to_list(length=None)
        
        # Calcular estatísticas
        total_features = len(features)
        total_groups = len(feature_groups)
        
        return {
            "total_features": total_features,
            "total_feature_groups": total_groups,
            "connections": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
