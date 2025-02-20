from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Dict, Any
from app.models.feature import Feature
from app.models.feature_group import FeatureGroup
from app.core.feature_processor import FeatureProcessor

router = APIRouter()

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Retorna métricas e estatísticas sobre o Feature Store
    """
    try:
        # Obter todas as features e grupos
        features = await Feature.find_all().to_list()
        feature_groups = await FeatureGroup.find_all().to_list()
        
        # Calcular estatísticas de tipos de features
        feature_types = {
            "numerical": 0,
            "categorical": 0,
            "temporal": 0
        }
        
        for feature in features:
            if feature.type in feature_types:
                feature_types[feature.type] += 1
            
        # Obter métricas de processamento do FeatureProcessor
        processor_metrics = FeatureProcessor.get_metrics()
        
        # Construir lista de atividades recentes
        recent_activities = []
        for feature in sorted(features, key=lambda x: x.created_at, reverse=True)[:5]:
            recent_activities.append({
                "action": f"Feature '{feature.name}' created",
                "timestamp": feature.created_at
            })
            
        for group in sorted(feature_groups, key=lambda x: x.created_at, reverse=True)[:5]:
            recent_activities.append({
                "action": f"Feature Group '{group.name}' created",
                "timestamp": group.created_at
            })
            
        # Ordenar atividades por timestamp
        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activities = recent_activities[:10]  # Manter apenas as 10 mais recentes
        
        return {
            "processedFeatures": processor_metrics.get("processed_count", 0),
            "totalFeatures": len(features),
            "processingRate": processor_metrics.get("processing_rate", 0),
            "lastProcessingTime": processor_metrics.get("last_processing_time"),
            "featureStats": feature_types,
            "recentActivity": recent_activities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
