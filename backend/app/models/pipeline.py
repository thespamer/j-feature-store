"""Models para feature pipelines."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class PipelineStatus(str, Enum):
    """Status possíveis para um pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TransformationType(str, Enum):
    """Tipos de transformação suportados."""
    SQL = "sql"
    PYTHON = "python"
    PANDAS = "pandas"

class ScheduleInterval(str, Enum):
    """Intervalos de agendamento suportados."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class PipelineConfig(BaseModel):
    """Configuração de um pipeline."""
    transformation_type: TransformationType
    source_query: str
    schedule_interval: ScheduleInterval
    custom_schedule: Optional[str] = None  # Cron expression para custom schedule
    parameters: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 3600
    retries: int = 3
    
class Pipeline(BaseModel):
    """Modelo para feature pipeline."""
    id: str
    name: str
    description: Optional[str] = None
    feature_group_id: str
    config: PipelineConfig
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    status: PipelineStatus = PipelineStatus.PENDING
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        """Configuração do modelo."""
        from_attributes = True

class PipelineRun(BaseModel):
    """Modelo para execução de pipeline."""
    id: str
    pipeline_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: PipelineStatus
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None  # Métricas como rows processed, latency, etc
    feature_versions: List[str]  # Versions of features updated in this run
