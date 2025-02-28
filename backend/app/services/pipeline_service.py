"""Serviço para gerenciamento de feature pipelines."""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
import pandas as pd
from croniter import croniter

from app.models.pipeline import (
    Pipeline, PipelineRun, PipelineConfig,
    PipelineStatus, TransformationType, ScheduleInterval
)
from app.core.config import settings
from app.services.feature_store import FeatureStore

class PipelineService:
    """Serviço para gerenciamento de pipelines."""
    
    def __init__(self, feature_store: FeatureStore):
        """Inicializa o serviço de pipeline."""
        self.feature_store = feature_store
        self.db = feature_store.db
        self._running_pipelines = {}
        
    async def create_pipeline(self, name: str, feature_group_id: str, config: PipelineConfig) -> Pipeline:
        """Cria um novo pipeline."""
        pipeline_dict = {
            "name": name,
            "feature_group_id": feature_group_id,
            "config": config.dict(),
            "created_at": datetime.utcnow(),
            "status": PipelineStatus.PENDING,
        }
        
        result = await self.db.pipelines.insert_one(pipeline_dict)
        pipeline_dict["id"] = str(result.inserted_id)
        
        # Agenda primeira execução
        await self._schedule_next_run(Pipeline(**pipeline_dict))
        
        return Pipeline(**pipeline_dict)
    
    async def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        """Obtém um pipeline pelo ID."""
        pipeline_data = await self.db.pipelines.find_one({"_id": ObjectId(pipeline_id)})
        if pipeline_data:
            pipeline_data["id"] = str(pipeline_data.pop("_id"))
            return Pipeline(**pipeline_data)
        return None
    
    async def list_pipelines(self, feature_group_id: Optional[str] = None) -> List[Pipeline]:
        """Lista todos os pipelines."""
        query = {}
        if feature_group_id:
            query["feature_group_id"] = feature_group_id
            
        pipelines = []
        async for pipeline_data in self.db.pipelines.find(query):
            pipeline_data["id"] = str(pipeline_data.pop("_id"))
            pipelines.append(Pipeline(**pipeline_data))
        return pipelines
    
    async def execute_pipeline(self, pipeline: Pipeline) -> PipelineRun:
        """Executa um pipeline."""
        # Cria registro de execução
        run_dict = {
            "pipeline_id": pipeline.id,
            "start_time": datetime.utcnow(),
            "status": PipelineStatus.RUNNING,
            "feature_versions": []
        }
        run_result = await self.db.pipeline_runs.insert_one(run_dict)
        run_dict["id"] = str(run_result.inserted_id)
        
        try:
            # Atualiza status do pipeline
            await self.db.pipelines.update_one(
                {"_id": ObjectId(pipeline.id)},
                {
                    "$set": {
                        "status": PipelineStatus.RUNNING,
                        "last_run_at": datetime.utcnow()
                    }
                }
            )
            
            # Executa transformação
            if pipeline.config.transformation_type == TransformationType.SQL:
                await self._execute_sql_transformation(pipeline)
            elif pipeline.config.transformation_type == TransformationType.PYTHON:
                await self._execute_python_transformation(pipeline)
            elif pipeline.config.transformation_type == TransformationType.PANDAS:
                await self._execute_pandas_transformation(pipeline)
            
            # Atualiza status como sucesso
            run_dict["status"] = PipelineStatus.COMPLETED
            run_dict["end_time"] = datetime.utcnow()
            
            await self.db.pipeline_runs.update_one(
                {"_id": run_result.inserted_id},
                {"$set": {
                    "status": PipelineStatus.COMPLETED,
                    "end_time": datetime.utcnow()
                }}
            )
            
            # Agenda próxima execução
            await self._schedule_next_run(pipeline)
            
        except Exception as e:
            # Atualiza status como falha
            error_message = str(e)
            run_dict["status"] = PipelineStatus.FAILED
            run_dict["error_message"] = error_message
            run_dict["end_time"] = datetime.utcnow()
            
            await self.db.pipeline_runs.update_one(
                {"_id": run_result.inserted_id},
                {"$set": {
                    "status": PipelineStatus.FAILED,
                    "error_message": error_message,
                    "end_time": datetime.utcnow()
                }}
            )
            
            await self.db.pipelines.update_one(
                {"_id": ObjectId(pipeline.id)},
                {
                    "$set": {
                        "status": PipelineStatus.FAILED,
                        "error_message": error_message
                    }
                }
            )
            
            raise
            
        return PipelineRun(**run_dict)
    
    async def _schedule_next_run(self, pipeline: Pipeline):
        """Agenda próxima execução do pipeline."""
        if pipeline.config.schedule_interval == ScheduleInterval.CUSTOM:
            if not pipeline.config.custom_schedule:
                raise ValueError("Custom schedule must be provided for CUSTOM interval")
            cron = croniter(pipeline.config.custom_schedule, datetime.utcnow())
            next_run = cron.get_next(datetime)
        else:
            intervals = {
                ScheduleInterval.HOURLY: timedelta(hours=1),
                ScheduleInterval.DAILY: timedelta(days=1),
                ScheduleInterval.WEEKLY: timedelta(weeks=1),
                ScheduleInterval.MONTHLY: timedelta(days=30),
            }
            next_run = datetime.utcnow() + intervals[pipeline.config.schedule_interval]
        
        await self.db.pipelines.update_one(
            {"_id": ObjectId(pipeline.id)},
            {"$set": {"next_run_at": next_run}}
        )
    
    async def _execute_sql_transformation(self, pipeline: Pipeline):
        """Executa transformação SQL."""
        async with self.feature_store.postgres_pool.acquire() as conn:
            # Executa query
            result = await conn.fetch(pipeline.config.source_query)
            
            # Converte para DataFrame
            df = pd.DataFrame(result)
            
            # Atualiza features
            await self._update_features(pipeline.feature_group_id, df)
    
    async def _execute_python_transformation(self, pipeline: Pipeline):
        """Executa transformação Python."""
        # Implementar execução segura de código Python
        pass
    
    async def _execute_pandas_transformation(self, pipeline: Pipeline):
        """Executa transformação Pandas."""
        # Implementar transformação com Pandas
        pass
    
    async def _update_features(self, feature_group_id: str, df: pd.DataFrame):
        """Atualiza features com dados transformados."""
        # Obtém features do grupo
        group = await self.feature_store.get_feature_group(feature_group_id)
        if not group:
            raise ValueError(f"Feature group {feature_group_id} not found")
            
        # Para cada feature no grupo
        for feature_id in group.features:
            feature = await self.feature_store.get_feature(feature_id)
            if not feature:
                continue
                
            # Se a coluna existe no DataFrame
            if feature.name in df.columns:
                # Insere valores com timestamp
                for _, row in df.iterrows():
                    await self.feature_store.insert_feature_value(
                        feature_id,
                        {
                            "value": row[feature.name],
                            "timestamp": datetime.utcnow()
                        }
                    )
