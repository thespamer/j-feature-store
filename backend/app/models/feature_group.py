"""Módulo de modelos de grupo de features."""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.models.feature import Feature, FeatureCreate

class FeatureGroup(BaseModel):
    """Modelo de grupo de features."""
    name: str
    description: Optional[str] = None
    entity_type: str
    features: List[str]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    version: int = 1

class FeatureGroupCreate(BaseModel):
    """Modelo para criação de grupo de features."""
    name: str
    description: Optional[str] = None
    entity_type: str
    features: List[FeatureCreate]
    metadata: Optional[Dict[str, Any]] = None

class FeatureGroupUpdate(BaseModel):
    """Modelo para atualização de grupo de features."""
    description: Optional[str] = None
    features: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
