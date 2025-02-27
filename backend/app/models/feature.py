"""Módulo de modelos de feature."""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ValidationRules(BaseModel):
    """Regras de validação para features."""
    allow_null: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    categorical_values: Optional[List[str]] = None
    regex_pattern: Optional[str] = None
    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None

class TransformationConfig(BaseModel):
    """Configuração de transformação para features."""
    type: str
    params: Optional[Dict[str, Any]] = None

class Feature(BaseModel):
    """Modelo de feature."""
    id: str
    name: str
    type: str
    description: Optional[str] = None
    validation_rules: Optional[ValidationRules] = None
    transformation: Optional[TransformationConfig] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    version: str = "1.0.0"
    status: str = "active"
    dependencies: Optional[List[str]] = None
    entity_id: Optional[str] = None
    feature_group_id: Optional[str] = None

class FeatureCreate(BaseModel):
    """Modelo para criação de feature."""
    name: str
    type: str
    description: Optional[str] = None
    validation_rules: Optional[ValidationRules] = None
    transformation: Optional[TransformationConfig] = None
    metadata: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    version: str = "1.0.0"
    entity_id: Optional[str] = None
    feature_group_id: Optional[str] = None

class FeatureUpdate(BaseModel):
    """Modelo para atualização de feature."""
    description: Optional[str] = None
    validation_rules: Optional[ValidationRules] = None
    transformation: Optional[TransformationConfig] = None
    metadata: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    version: Optional[str] = None

class FeatureValue(BaseModel):
    """Modelo de valor de feature."""
    id: Optional[str] = None
    feature_id: str
    value: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
