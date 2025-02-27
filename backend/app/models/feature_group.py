"""Módulo de modelos de grupo de features."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.models.feature import Feature, FeatureCreate

class FeatureGroup(BaseModel):
    """Modelo de grupo de features."""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    entity_type: str
    features: List[str]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    version: int = 1
    tags: List[str] = Field(default_factory=list, description="Tags para categorização")
    frequency: Optional[str] = Field(None, description="Frequência de atualização (e.g., 'daily', 'hourly')")
    owner: Optional[str] = Field(None, description="Responsável pelo feature group")
    status: str = Field("active", description="Status do feature group (active, deprecated, etc)")
    schema_version: str = Field("1.0", description="Versão do schema do feature group")
    dependencies: Optional[List[str]] = Field(None, description="IDs de outros feature groups dependentes")
    offline_enabled: bool = Field(True, description="Se disponível para treinamento offline")
    online_enabled: bool = Field(True, description="Se disponível para inferência online")

class FeatureGroupCreate(BaseModel):
    """Modelo para criação de grupo de features."""
    name: str
    description: Optional[str] = None
    entity_type: str
    features: List[str] = []
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    frequency: Optional[str] = None
    owner: Optional[str] = None
    offline_enabled: bool = True
    online_enabled: bool = True

class FeatureGroupUpdate(BaseModel):
    """Modelo para atualização de grupo de features."""
    description: Optional[str] = None
    features: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    frequency: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    offline_enabled: Optional[bool] = None
    online_enabled: Optional[bool] = None
