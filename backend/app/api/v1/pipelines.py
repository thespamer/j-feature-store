"""API endpoints para feature pipelines."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.models.pipeline import Pipeline, PipelineConfig
from app.services.pipeline_service import PipelineService
from app.dependencies import get_pipeline_service

router = APIRouter()

@router.post("/pipelines", response_model=Pipeline)
async def create_pipeline(
    name: str,
    feature_group_id: str,
    config: PipelineConfig,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """Cria um novo pipeline."""
    try:
        return await pipeline_service.create_pipeline(name, feature_group_id, config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pipelines", response_model=List[Pipeline])
async def list_pipelines(
    feature_group_id: Optional[str] = None,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """Lista todos os pipelines."""
    return await pipeline_service.list_pipelines(feature_group_id)

@router.get("/pipelines/{pipeline_id}", response_model=Pipeline)
async def get_pipeline(
    pipeline_id: str,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """Obtém um pipeline pelo ID."""
    pipeline = await pipeline_service.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline não encontrado")
    return pipeline

@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: str,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """Executa um pipeline manualmente."""
    pipeline = await pipeline_service.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline não encontrado")
        
    try:
        await pipeline_service.execute_pipeline(pipeline)
        return {"message": "Pipeline executado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
