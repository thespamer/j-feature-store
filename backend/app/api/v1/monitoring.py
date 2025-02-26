"""API endpoints para monitoramento."""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.services.feature_store import FeatureStore
from datetime import datetime
from app.core.store import get_feature_store
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
import asyncpg

router = APIRouter()

def get_store() -> FeatureStore:
    """Dependência para obter a instância do FeatureStore."""
    return get_feature_store()

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

async def check_connections_new():
    """Check all service connections."""
    feature_store = get_feature_store()
    status = {
        "mongodb": False,
        "redis": False,
        "postgres": False
    }
    
    try:
        # Check MongoDB
        if isinstance(feature_store.mongo_client, AsyncIOMotorClient):
            await feature_store.mongo_client.admin.command('ping')
            status["mongodb"] = True
    except Exception as e:
        print(f"MongoDB error: {e}")

    try:
        # Check Redis
        if isinstance(feature_store.redis_client, Redis):
            await feature_store.redis_client.ping()
            status["redis"] = True
    except Exception as e:
        print(f"Redis error: {e}")

    try:
        # Check Postgres
        if isinstance(feature_store.postgres_pool, asyncpg.Pool):
            async with feature_store.postgres_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            status["postgres"] = True
    except Exception as e:
        print(f"Postgres error: {e}")

    return status

@router.get("/monitoring/metrics")
async def get_metrics(store: FeatureStore = Depends(get_store)) -> Dict[str, Any]:
    """Obtém métricas do feature store."""
    try:
        metrics = {
            "total_features": await store.count_features(),
            "total_feature_groups": await store.count_feature_groups(),
            "total_feature_values": await store.count_feature_values(),
            "storage_usage": await store.get_storage_usage(),
            "last_update": await store.get_last_update_time()
        }
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/health")
async def health_check(store: FeatureStore = Depends(get_store)) -> Dict[str, str]:
    """Verifica a saúde do sistema."""
    try:
        status = await store.check_health()
        return {"status": "healthy" if status else "unhealthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/monitoring/alerts")
async def get_alerts(store: FeatureStore = Depends(get_store)) -> List[Dict[str, Any]]:
    """Obtém alertas ativos."""
    try:
        return await store.get_active_alerts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/performance")
async def get_performance_metrics(store: FeatureStore = Depends(get_store)) -> Dict[str, Any]:
    """Obtém métricas de performance."""
    try:
        return await store.get_performance_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/feature-stats/{feature_id}")
async def get_feature_stats(feature_id: str, store: FeatureStore = Depends(get_store)) -> Dict[str, Any]:
    """Obtém estatísticas de uma feature."""
    try:
        stats = await store.get_feature_statistics(feature_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Feature não encontrada")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check_new():
    """Health check endpoint."""
    try:
        status = await check_connections_new()
        return {
            "status": "healthy" if all(status.values()) else "unhealthy",
            "services": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

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
