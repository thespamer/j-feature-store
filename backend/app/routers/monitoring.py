from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    return {
        "total_features": 0,
        "total_feature_groups": 0,
        "total_entities": 0
    }
